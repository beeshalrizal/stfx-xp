------------------------------------------------------------------------------------------------
-- Calculate PnL of Open Trades --
-- TODO
-- * Fees not incorporated in PnL calculations
-- * PnL gets buggy when trader removes a lot of collateral when they're winning
------------------------------------------------------------------------------------------------

-- Formats trades human-readable
-- Numbers trades according to user, side, and token
with trades_tmp as (
SELECT trades.time, account, ROUND(price,8) as price, key,
    ( 
        CASE indexToken
        WHEN '0x82af49447d8a07e3bd95bd0d56f35241523fbab1' THEN 'WETH'
        WHEN '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f' THEN 'WBTC'
        WHEN '0xf97f4df75117a78c1a5a0dbb814af92458539fb4' THEN 'LINK'
        WHEN '0xfa7f8980b0f1e64a2062791cc3b0871572f1f7f0' THEN 'UNI'
        -- ELSE CONCAT('0x',substring(`data` FROM 91 FOR 40))
        END
    ) as token,
    position_side, 
    IF(position_side = 'LONG', ROUND(size,8), 0) as long_size,
    IF(position_side = 'SHORT', ROUND(size,8), 0) as short_size,
    ROUND(SUM(size) OVER (PARTITION BY key ORDER BY trades.time),7) as running_total_size,
    -- ROUND(SUM(size) OVER (PARTITION BY account, trades.indexToken, position_side ORDER BY trades.time),7) as running_total_size,
    collatDelta,
    ROW_NUMBER() OVER (PARTITION BY key ORDER BY indexToken, time) as id
    -- ROW_NUMBER() OVER (PARTITION BY account, trades.indexToken, position_side ORDER BY indexToken, time) as id
FROM (
    -- There are missing txns (eg. 0x774450ccb7892791d32dc757852363e160e05fc48422021c891aa4ce2e8cae61)
    SELECT evt_block_time as time, key, account, indexToken, price/1e30 as price, sizeDelta/1e30 as size, if(`isLong`, 'LONG', 'SHORT') as position_side, collateralDelta/1e30 as collatDelta 
    FROM gmx_arbitrum.Vault_evt_IncreasePosition
    UNION ALL
    SELECT evt_block_time as time, key, account, indexToken, markPrice/1e30 as price, -size/1e30 as size, if(`isLong`, 'LONG', 'SHORT')  as position_side, NULL as collatDelta
    FROM gmx_arbitrum.Vault_evt_LiquidatePosition
    UNION ALL
    SELECT evt_block_time as time, key, account, indexToken, price/1e30 as price, -sizeDelta/1e30 as size, if(`isLong`, 'LONG', 'SHORT')  as position_side, -collateralDelta/1e30 as collatDelta 
    FROM gmx_arbitrum.Vault_evt_DecreasePosition
    ) as trades
-- WHERE account = '0xb5beb7b5aa8430a43a516d583e498ce1788446b9' -- DEBUG
ORDER BY id desc
),
 
-- Group trades together
trades_tmp2 as (
    SELECT tt.*,
        COUNT(CASE WHEN running_total_size > 0 THEN NULL ELSE 1 END) OVER (PARTITION BY key ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) as grp
    FROM trades_tmp tt
    ORDER BY id
),

-- Calculate running_collat, running_qty
-- Flag open/closed trades
-- Append recent price
trades_tmp3 as (
    SELECT tt2.time, tt2.key, tt2.account, tt2.price, tt2.token, tt2.position_side, tt2.id, tt2.long_size, tt2.short_size, tt2.running_total_size, tt2.collatDelta,
        SUM(tt2.collatDelta) OVER (PARTITION BY tt2.key ORDER BY tt2.time) as running_collat,
        SUM(CASE WHEN tt2.position_side = "LONG" THEN tt2.long_size/tt2.price ELSE tt2.short_size/tt2.price END) OVER (PARTITION BY tt2.key ORDER BY tt2.time) as running_qty,
        (CASE WHEN tt3.grp is NULL THEN "OPEN" ELSE "CLOSED" END) as state,
        (CASE tt2.token 
            WHEN 'WBTC' THEN (SELECT price FROM prices.usd WHERE minute >= NOW() - interval '1 day'and symbol = 'WBTC' ORDER BY minute desc limit 1)
            WHEN 'WETH' THEN (SELECT price FROM prices.usd WHERE minute >= NOW() - interval '1 day'and symbol = 'WETH' ORDER BY minute desc limit 1)
            WHEN 'UNI' THEN (SELECT price FROM prices.usd WHERE minute >= NOW() - interval '1 day'and symbol = 'UNI' ORDER BY minute desc limit 1)
            WHEN 'LINK' THEN (SELECT price FROM prices.usd WHERE minute >= NOW() - interval '1 day'and symbol = 'LINK' ORDER BY minute desc limit 1)
        END) as recent_price
    FROM trades_tmp2 tt2 LEFT OUTER JOIN 
        -- All groups that have a running_total_size of 0 are closed trades
        (SELECT account, token, position_side, grp FROM trades_tmp2 WHERE running_total_size=0) tt3
        on tt2.account = tt3.account
        and tt2.grp = tt3.grp
        and tt2.token = tt3.token
        and tt2.position_side = tt3.position_side
    WHERE tt3.grp is NULL
    ORDER BY tt2.account, tt2.token, time asc
),

-- Calculate avg_price and leverage
trades_tmp4 as (
SELECT tt3.*, 
    running_total_size/running_qty as avg_price, 
    running_total_size/running_collat as leverage
FROM trades_tmp3 tt3
)

-- Get most recent trade state
-- Calculate pnl and pnl%
SELECT tmp4.time, 
    tmp4.account,
    ROUND(tmp4.price,2) as price,
    tmp4.token,
    tmp4.position_side,
    ROUND(tmp4.long_size,2) as long_size,
    ROUND(tmp4.short_size,2) as short_size,
    ROUND(tmp4.running_total_size,2) as running_total_size,
    -- ROUND(tmp4.collatDelta,2) as collatDelta,
    ROUND(tmp4.running_collat,2) as running_collat,
    -- ROUND(tmp4.running_qty,2) as running_qty,
    ROUND(tmp4.recent_price,2) as recent_price,
    ROUND(tmp4.avg_price,2) as avg_price,
    ROUND(tmp4.leverage,2) as leverage,
    ROUND((CASE tmp4.position_side 
    WHEN 'LONG' THEN running_collat*(recent_price/avg_price-1)*leverage
    WHEN 'SHORT' THEN running_collat*(avg_price/recent_price-1)*leverage END),2) as pnl,
    ROUND((CASE tmp4.position_side
    WHEN 'LONG' THEN (recent_price/avg_price-1)*leverage
    WHEN 'SHORT' THEN (avg_price/recent_price-1)*leverage END),4) as pnl_pct
FROM trades_tmp4 tmp4 INNER JOIN (
    SELECT account, token, position_side, MAX(id) as id_max from trades_tmp4 group by account, token, position_side) tmp4_max
    ON tmp4.account = tmp4_max.account
    AND tmp4.token = tmp4_max.token
    AND tmp4.position_side = tmp4_max.position_side
    AND tmp4.id = tmp4_max.id_max
WHERE running_collat > 0
-- [BUG] Edge-case when trader reduces a lot of their position when winning
AND  ROUND((CASE tmp4.position_side
    WHEN 'LONG' THEN (recent_price/avg_price-1)*leverage
    WHEN 'SHORT' THEN (avg_price/recent_price-1)*leverage END),4) > -1
ORDER BY (CASE tmp4.position_side 
    WHEN 'LONG' THEN running_collat*(recent_price/avg_price-1)*leverage
    WHEN 'SHORT' THEN running_collat*(avg_price/recent_price-1)*leverage END) desc
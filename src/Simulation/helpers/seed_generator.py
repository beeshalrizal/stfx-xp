# type: ignore
from scipy.stats import truncnorm


"""
    with
        vault_keys as (
            SELECT
            account,
            "key" as trade_key,
            recent_vaults.manager_address,
            recent_vaults.entry_price,
            recent_vaults.exit_price,
            recent_vaults.leverage,
            recent_vaults.position_side,
            recent_vaults.manager
            from
            gmx_arbitrum.Vault_evt_IncreasePosition AS increase_position
            JOIN query_1823027 as recent_vaults ON increase_position.account = recent_vaults.vault_address
        ),
    pnls as (
            select
            *
            FROM
            (
                SELECT
                'close' as type,
                --   date_trunc('day', evt_block_time) as time,
                cast(realisedPnl as double) / 1e30 as pnl,
                "key" as position_key,
                averagePrice / 1e30 as price,
                size / 1e30 as size
                FROM
                gmx_arbitrum.Vault_evt_ClosePosition as closed_position
                UNION ALL
                SELECT
                'liq' as type,
                --   date_trunc('day', evt_block_time) as time,
                - cast(collateral as double) / 1e30 as pnl,
                "key" as position_key,
                markPrice / 1e30 as price,
                size / 1e30 as size
                FROM
                gmx_arbitrum.Vault_evt_LiquidatePosition as liquidate_position
            ) as all_pnls
            JOIN vault_keys on vault_keys.trade_key = all_pnls.position_key
        ),
    pctg as (
            select
            type,
            price,
            entry_price,
            position_side,
            case
                when position_side = 'LONG' then (price - entry_price) / price * 100
                else (entry_price - price) / entry_price * 100
            end as roi,
            size,
            pnl,
            leverage
            from
            pnls
        )
        --   select * from pctg
        --   limit 100
        select
        stddev(roi) as std,
        avg(roi) as avg,
        max(roi) as max,
        min(roi) as min
    from
    pctg
"""

PNL_MEAN = 0.0025
PNL_SD = 21.8815
PNL_MAX = 100
PNL_MIN = -100


def getPnlPctgSeed(samples: int):
    return _getTruncNormal(PNL_MEAN, PNL_SD, PNL_MIN, PNL_MAX, samples)


FUNDS_MEAN = 55
FUNDS_SD = 25
FUNDS_MAX = 100
FUNDS_MIN = 10


def getFundsPctgSeed(samples: int):
    return _getTruncNormal(FUNDS_MEAN, FUNDS_SD, FUNDS_MIN, FUNDS_MAX, samples)


"""
    Use trunc normal with to draw a normal distribution between lower and upper bounds
    Use rvs to specify number of samples
"""


def _getTruncNormal(mean=0, sd=1, lower=0, upper=10, samples=1000):
    samples = truncnorm.rvs(
        (lower - mean) / sd, (upper - mean) / sd, loc=mean, scale=sd, size=samples
    )

    return samples

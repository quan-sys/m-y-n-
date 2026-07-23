NEITHER_ABSOLUTE_VALUATION_BLOCKED

# Sprint 9.0 price-adjustment probe

Probe date: 2026-07-23
Installed package: `vnstock==4.0.3`
Provider: VCI
Sample tickers: VNM, FPT, HPG

This is a provider-metadata probe only. It does not create a market-capitalisation, valuation, or portfolio artifact, and it does not alter the cached price series.

## N1. Verdict line

`NEITHER_ABSOLUTE_VALUATION_BLOCKED`

There is no direct raw-price switch. VCI exposes useful dated corporate-action fields, but the sample is not complete enough to reconstruct a cumulative adjustment factor: HPG has a rights issue with a ratio and ex-rights date but no subscription price, and FPT has a bonus issue ratio with no ex-rights date.

## N2. `Quote.history` signature, docstring, and parameters

`inspect.signature(vnstock.Quote.history)`, verbatim:

```text
(self, symbol: Optional[str] = None, start: str = None, end: str = None, interval: str = <TimeFrame.DAY_1: '1D'>, **kwargs: Any) -> pandas.core.frame.DataFrame
```

`vnstock.Quote.history.__doc__`, verbatim:

```text

Load historical OHLC data for the symbol.
Tải dữ liệu OHLC lịch sử cho mã chứng khoán.

Args:
    symbol (str, optional): Stock symbol. Mã chứng khoán.
    start (str): Start time in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.
                Thời gian bắt đầu định dạng YYYY-MM-DD hoặc YYYY-MM-DD HH:MM:SS.
    end (str): End time in format YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.
              Thời gian kết thúc định dạng YYYY-MM-DD hoặc YYYY-MM-DD HH:MM:SS.
    interval (str, optional): Data interval (1m, 5m, 15m, 30m, 1H, D, 1W, 1M).
                             Khoảng thời gian dữ liệu (1m, 5m, 15m, 30m, 1H, D, 1W, 1M).

Returns:
    pandas.DataFrame: Historical price data. Dữ liệu giá lịch sử.

Examples:
    >>> quote = Quote(symbol="VCI", source="vci")
    >>> df = quote.history(start="2024-01-01", end="2024-04-18")
    >>> df = quote.history(symbol="FPT", start="2024-01-01", end="2024-04-18", interval=TimeResolutions.WEEKLY)
    >>> df = quote.history(symbol="FPT", start="2024-01-01 09:00:00", end="2024-01-01 14:30:00", interval=TimeResolutions.MINUTE_5)
```

Every parameter:

| parameter | default / annotation |
|---|---|
| `self` | instance |
| `symbol` | `Optional[str] = None` |
| `start` | `str = None` |
| `end` | `str = None` |
| `interval` | `str = <TimeFrame.DAY_1: '1D'>` |
| `**kwargs` | `Any` |

The delegated VCI implementation has this signature:

```text
(self, start: Optional[str] = None, end: Optional[str] = None, interval: Optional[str] = '1D', to_df: Optional[bool] = True, show_log: Optional[bool] = False, count_back: Optional[int] = None, floating: Optional[int] = 2, length: Union[str, int, NoneType] = None) -> pandas.core.frame.DataFrame
```

Adjustment-related parameters found: **none**. Neither the unified signature nor the VCI implementation exposes `adjust`, `adjusted`, `adj`, `price_type`, `raw`, or an equivalent selector.

## Public methods and attributes

Public names enumerated on the VNM `vnstock.Quote(source="VCI", symbol="VNM")` object:

```text
history
intraday
ohlcv
price_depth
provider
random_agent
show_log
source
symbol
```

Public names enumerated on the VNM `vnstock.Company(source="VCI", symbol="VNM")` object:

```text
affiliate
capital_history
events
history
info
insider_trading
news
officers
overview
ownership
provider
random_agent
shareholders
show_log
source
subsidiaries
symbol
```

Relevant public methods found:

- `events`: exists and returns a frame.
- `capital_history`: exists on the unified object, but VCI does not implement it. Calling it for VNM landed as `RetryError[<Future ... raised NotImplementedError>]`; the VCI provider object's public-method enumeration contains no `capital_history`.
- `dividends`: does not exist.
- `actions`: does not exist.
- `corporate_action`: does not exist.

## N3. Relevant method return columns and dumps

### `Company.events()` — VNM

Full returned column list:

```text
['id', 'event_name_vi', 'event_name_en', 'ticker', 'event_code', 'event_title_vi', 'event_title_en', 'display_date1', 'display_date2', 'public_date', 'start_date', 'end_date', 'action_type_vi', 'action_type_en', 'category', 'record_date', 'exright_date', 'payout_date', 'value_per_share', 'exercise_ratio', 'issue_date']
```

First 10 rows, verbatim from the returned frame:

```text
                      id                       event_name_vi                             event_name_en ticker event_code                                                      event_title_vi                                                                     event_title_en       display_date1       display_date2 public_date          start_date            end_date action_type_vi action_type_en                  category record_date exright_date         payout_date  value_per_share  exercise_ratio issue_date
6a503b2f3711162a7e7841ca Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS              Công ty TNHH MTV Đầu Tư SCIC - Đăng kí Mua 400,000 VNM   SCIC Investment One Member Company Limited - Subscribe to Buy 400,000 VNM shares 2026-07-14T00:00:00 2026-07-09T00:00:00  2026-07-09 2026-07-14T00:00:00 2026-08-12T00:00:00            Mua            Buy MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
6a333a0ae56b40f0537015e0            Trả cổ tức bằng tiền mặt                             Cash Dividend    VNM        DIV                   Trả cổ tức bằng tiền mặt - Đợt 2 2025 - 1,850 VND                                         Cash Dividend - Interim 2 2025 - 1,850 VND 2026-06-26T00:00:00 2026-06-19T00:00:00  2026-06-19                 NaN                 NaN            NaN            NaN                  DIVIDEND  2026-06-29   2026-06-26 2026-07-17T00:00:00           1850.0           0.185        NaN
6a1a2e226c972745c9ee889d Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS            Công ty TNHH MTV Đầu Tư SCIC - Đăng kí Mua 1,000,000 VNM SCIC Investment One Member Company Limited - Subscribe to Buy 1,000,000 VNM shares 2026-06-03T00:00:00 2026-05-28T00:00:00  2026-05-28 2026-06-03T00:00:00 2026-07-02T00:00:00            Mua            Buy MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
69d6f11a714770f525e21d29 Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS       Platinum Victory Private Limited - Đăng kí Bán 52,551,922 VNM               Platinum Victory Pte. Ltd. - Subscribe to Sell 52,551,922 VNM shares 2026-04-13T00:00:00 2026-05-12T00:00:00  2026-05-12 2026-04-13T00:00:00 2026-05-12T00:00:00            Bán           Sell MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
69eab80e9a7ad236002b1850 Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS            Pension Reserves Investment Trust Fund - Đăng kí Mua VNM               Pension Reserves Investment Trust Fund - Subscribe to Buy VNM shares 2026-04-14T00:00:00 2026-04-22T00:00:00  2026-04-22 2026-04-14T00:00:00 2026-04-14T00:00:00            Mua            Buy MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
69eab80e9a7ad236002b184f Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS PZENA EMERCING MARKETS FOCUSED VALUE FUND - UCITS - Đăng kí Mua VNM    PZENA EMERCING MARKETS FOCUSED VALUE FUND - UCITS - Subscribe to Buy VNM shares 2026-04-14T00:00:00 2026-04-22T00:00:00  2026-04-22 2026-04-14T00:00:00 2026-04-14T00:00:00            Mua            Buy MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
69eab80e9a7ad236002b184e Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS            PZENA EMERGING MARKETS VALUE FUND - MF - Đăng kí Mua VNM               PZENA EMERGING MARKETS VALUE FUND - MF - Subscribe to Buy VNM shares 2026-04-14T00:00:00 2026-04-22T00:00:00  2026-04-22 2026-04-14T00:00:00 2026-04-14T00:00:00            Mua            Buy MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
69a8ccc1f2d24c49e81349ae Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS       Platinum Victory Private Limited - Đăng kí Bán 52,551,922 VNM               Platinum Victory Pte. Ltd. - Subscribe to Sell 52,551,922 VNM shares 2026-03-09T00:00:00 2026-04-08T00:00:00  2026-04-08 2026-03-09T00:00:00 2026-04-07T00:00:00            Bán           Sell MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
6972bf6024a1c5199e91d8b8 Giao dịch nội bộ: Giao dịch tổ chức Director Deal: Institutional transactions    VNM      DDINS      Platinum Victory Private Limited - Đăng kí Bán 125,761,922 VNM              Platinum Victory Pte. Ltd. - Subscribe to Sell 125,761,922 VNM shares 2026-01-28T00:00:00 2026-03-04T00:00:00  2026-03-04 2026-01-28T00:00:00 2026-02-26T00:00:00            Bán           Sell MAJOR_SHAREHOLDER_TRADING         NaN          NaN                 NaN              NaN             NaN        NaN
69a0e433f24a113a2ff1870f                Đại hội Đồng Cổ đông                    Annual General Meeting    VNM       AGME                                VNM - Tổ chức ĐHĐCĐ thường niên 2026                                                               VNM - Holds 2026 AGM 2026-04-22T00:00:00 2026-03-17T00:00:00  2026-02-27                 NaN                 NaN            NaN            NaN       SHAREHOLDER_MEETING  2026-03-18   2026-03-17                 NaN              NaN             NaN 2026-04-22
```

### `Company.events()` — FPT

Full returned column list:

```text
['id', 'event_name_vi', 'event_name_en', 'ticker', 'event_code', 'event_title_vi', 'event_title_en', 'display_date1', 'display_date2', 'public_date', 'start_date', 'end_date', 'action_type_vi', 'action_type_en', 'category', 'record_date', 'exright_date', 'exercise_ratio', 'payout_date', 'value_per_share', 'issue_date', 'listing_date']
```

The unfiltered first 10 returned rows included two `ISS` rows in positions 8 and 9:

```text
                      id      event_name_vi event_name_en ticker event_code                                      event_title_vi                event_title_en       display_date1       display_date2 public_date record_date exright_date  exercise_ratio category
6a309747e56b40f0536c38e0 Phát hành cổ phiếu   Share Issue    FPT        ISS Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.1% Share Issue - ESOP ratio 0.1% 2026-06-24T00:00:00 2026-06-29T00:00:00  2026-06-29  2026-06-24   2026-06-24         0.00135 DIVIDEND
69e6c30a9a7ad2360023b0c2 Phát hành cổ phiếu   Share Issue    FPT        ISS Phát hành cổ phiếu - Phát hành cho CBCNV tỉ lệ 0.5% Share Issue - ESOP ratio 0.5% 2026-06-24T00:00:00 2026-06-29T00:00:00  2026-06-29  2026-06-24   2026-06-24         0.00499 DIVIDEND
```

### `Company.events()` — HPG

Full returned column list:

```text
['id', 'event_name_vi', 'event_name_en', 'ticker', 'event_code', 'event_title_vi', 'event_title_en', 'display_date1', 'display_date2', 'public_date', 'issue_date', 'category', 'start_date', 'end_date', 'action_type_vi', 'action_type_en', 'record_date', 'exright_date', 'listing_date', 'exercise_ratio', 'payout_date', 'value_per_share']
```

The unfiltered first 10 returned rows included the following `ISS` row in position 3 and `DIV` row in position 4:

```text
                      id            event_name_vi event_name_en ticker event_code                                                   event_title_vi                                event_title_en       display_date1       display_date2 public_date record_date exright_date listing_date  exercise_ratio payout_date  value_per_share category
69eab80f9a7ad236002b1866      Phát hành cổ phiếu   Share Issue    HPG        ISS Phát hành cổ phiếu - Trả Cổ tức bằng Cổ phiếu tỉ lệ 10.0% Share Issue - Stock dividend ratio 10.0% 2026-05-25T00:00:00 2026-05-15T00:00:00  2026-05-15  2026-05-26   2026-05-25   2026-07-15             0.1         NaN              NaN DIVIDEND
69f2a0f5db487120c68d393b Trả cổ tức bằng tiền mặt Cash Dividend    HPG        DIV                    Trả cổ tức bằng tiền mặt - Cả năm 2025 - 500 VND           Cash Dividend - Year 2025 - 500 VND 2026-05-11T00:00:00 2026-05-05T00:00:00  2026-05-05  2026-05-12   2026-05-11          NaN            0.05  2026-06-03            500.0 DIVIDEND
```

`events` is the only dividends/events/actions-named method that exists. Its returned columns are listed above for every sample ticker. `capital_history` returned no frame because it is not implemented by VCI.

## Why the verdict is `NEITHER_ABSOLUTE_VALUATION_BLOCKED`

The VCI event frames expose:

- `exright_date`, the effective boundary at which an adjustment applies;
- `exercise_ratio`, a structured stock issue/bonus ratio;
- `value_per_share`, a structured cash-dividend amount;
- `event_code` and `category`, which distinguish `ISS` and `DIV` events.

The sample contains many usable populated ratios, including VNM's known 20% bonus issue:

```text
eventTitleEn                          exrightDate         exerciseRatio valuePerShare
Share Issue - Bonus Issue ratio 20.0% 2020-09-29T00:00:00           0.2
```

However, dumping all `DIV,ISS` rows for the three samples exposed missing inputs:

```text
ticker eventTitleEn                           exrightDate         exerciseRatio valuePerShare
HPG    Share Issue - Rights issue ratio 20.0% 2017-06-16T00:00:00           0.2
FPT    Share Issue - Bonus Issue ratio 10.0%                                  0.1
```

The HPG rights issue needs its subscription price to calculate the theoretical ex-rights adjustment, but `value_per_share` is blank. The FPT bonus issue has a ratio but no `exright_date`. Several FPT ESOP rows also return `exercise_ratio = 0.0`. Therefore these events cannot produce a complete, unambiguous per-date cumulative adjustment factor for the sample. A partial set of usable actions is not enough for the `ADJUSTMENT_FACTOR_DERIVABLE` verdict. No direct raw-price series selector was found, so the required verdict is `NEITHER_ABSOLUTE_VALUATION_BLOCKED`.

## N4. Raw/adjusted five-row comparison

Not applicable: no raw/adjusted toggle exists in either `vnstock.Quote.history` or the delegated VCI `history` method, so there are not two provider-selected close series to place side by side.

## Provider limitations observed

- VCI `events()` defaults to a ten-year date window and a 50-row first page in `vnstock==4.0.3`. Reconstructing a complete series would require explicit pagination and date coverage checks; that implementation is outside this probe.
- VCI does not implement `Company.capital_history()` in this package version.
- VCI exposes some structured corporate-action inputs for VNM/FPT/HPG, but the missing rights-issue price and missing ex-rights date are already sufficient to block reconstruction for the sample.

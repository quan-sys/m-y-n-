# Sprint 6 annual-history root cause

## Scope and evidence

This finding was established before any Sprint 6 extended-history fetch. The installed package is `vnstock 4.0.3` at `D:\thanh quan\Lib\site-packages\vnstock`.

The production client constructs `Finance` with `get_all=True`, but then calls the public statement method without a history limit. Verbatim from `src/data/finance_client.py:408-417`:

```python
        finance = _quiet_call(
            finance_class,
            source=self.provider,
            symbol=ticker,
            period=period,
            get_all=True,
            show_log=False,
        )
        method = getattr(finance, _STATEMENT_METHODS[statement_type])
        raw = _quiet_call(method, period=period, lang="en", dropna=False, show_log=False)
```

The installed wrapper stores and forwards `get_all` at construction. Verbatim from `D:\thanh quan\Lib\site-packages\vnstock\api\financial.py:43-63`:

```python
        # Store parameters for later use
        self.source = source
        self.symbol = symbol if symbol else ""
        self.period = period
        self.get_all = get_all
        self.show_log = show_log

        # Validate the source to only accept vci or kbs
        if source.lower() not in ["kbs", "vci"]:
            raise ValueError(
                "Lớp Finance chỉ nhận giá trị tham số source là 'VCI' hoặc 'KBS'."
            )

        # BaseAdapter will discover vnstock.explorer.<real_source>.financial
        # and pass only the kwargs its __init__ accepts (symbol, period, get_all, show_log).
        super().__init__(
            source=source,
            symbol=symbol,
            period=period,
            get_all=get_all,
            show_log=show_log,
        )
```

However, the three public VCI statement methods do not expose `get_all` or `limit`; for example, the balance-sheet path is verbatim from `D:\thanh quan\Lib\site-packages\vnstock\explorer\vci\financial.py:538-559`:

```python
    def balance_sheet(
        self,
        period: Optional[str] = None,
        lang: Optional[str] = "en",
        dropna: Optional[bool] = True,
        show_log: Optional[bool] = False,
    ) -> pd.DataFrame:
```

```python
        return self._get_financial_report(
            "balance_sheet", period=period, lang=lang, dropna=dropna, show_log=show_log
        )
```

`income_statement` and `cash_flow` have the same omission at `D:\thanh quan\Lib\site-packages\vnstock\explorer\vci\financial.py:562-587` and `:590-610` respectively. The internal report gateway accepts `limit` and passes it onward. Verbatim from `D:\thanh quan\Lib\site-packages\vnstock\explorer\vci\financial.py:496-520`:

```python
    def _get_financial_report(
        self,
        report_type: str,
        period: Optional[str] = None,
        lang: Optional[str] = "en",
        mode: Optional[str] = "final",
        style: Optional[str] = "readable",
        get_all: Optional[bool] = False,
        dropna: Optional[bool] = True,
        show_log: Optional[bool] = False,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
```

```python
        df = self._get_report(
            report_type=report_type,
            lang=lang,
            mode=mode,
            style=style,
            get_all=get_all,
            show_log=show_log,
            limit=limit,
            period=period,
        )
```

The VCI request layer converts an omitted limit to four. Verbatim from `D:\thanh quan\Lib\site-packages\vnstock\explorer\vci\financial.py:296-310`:

```python
        self,
        report_type: Union[str, None] = None,
        lang: Optional[str] = "en",
        show_log: Optional[bool] = False,
        mode: Optional[str] = "final",
        style: Optional[str] = "readable",
        get_all: Optional[bool] = False,
        period: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
```

```python
        # Baseline limit
        effective_limit = limit if limit is not None else 4
```

## Root cause

`get_all=True` controls field selection, not history depth. The production call uses a public statement method that does not pass `limit`; therefore `_get_financial_report` receives `limit=None`, and `_get_report` converts that to `effective_limit=4`. This is why the production cache stored four annual periods even though `get_all=True` was set.

## Exact minimal production change

For `period == "year"` only, call the installed VCI provider's existing `_get_financial_report` gateway with the existing statement report type and `limit=100`, while preserving `lang="en"`, `dropna=False`, `show_log=False`, and `get_all=True`. Keep the current public-method call unchanged for `period == "quarter"`. The provider remains VCI; normalization, `item_id` mapping, and the 90-day annual availability lag remain unchanged. The already completed probe demonstrates that this exact parameter returns annual periods 2018-2025 for all five probed tickers and all three statements.

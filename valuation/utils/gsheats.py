import re
import gspread
import pandas as pd

from valuation.utils.data import standardize_date


class Sheet:

    def __init__(self, sheet: pd.DataFrame) -> None:

        if not isinstance(sheet, pd.DataFrame):
            sheet = pd.DataFrame(sheet)

        self.sheet = sheet.copy()
        self.sheet.index = self.sheet[self.sheet.iloc[:, 0].name]
        del self.sheet[self.sheet.iloc[:, 0].name]
        self.sheet = self.sheet.apply(pd.to_numeric, errors='coerce')

    def __repr__(self) -> str:
        return self.sheet.__repr__()

    def __str__(self) -> str:
        return self.sheet.__repr__()

    def __getitem__(self, key: str | tuple | list) -> pd.DataFrame:

        if len(key) == 0:
            return self.sheet
        elif isinstance(key, list) or (not isinstance(key, tuple) and key in self.sheet.columns):
            return self.sheet.loc[:, key]
        elif not isinstance(key, tuple) and key in self.sheet.index:
            non_metric_cols = [c for c in self.sheet.columns if c != 'Metric']
            return self.sheet.loc[self.sheet.index == key, non_metric_cols]
        elif isinstance(key, tuple) and len(key) == 2:
            column_key = key[0] if key[0] in self.sheet.columns else key[1]
            row_key = key[0] if key[0] not in self.sheet.columns else key[1]
            return self.sheet.loc[self.sheet.index == row_key, column_key].values[0]

        raise IndexError("Unable to resolve index {} in sheet".format(key))

    def columns(self) -> list[str]:
        return list(self.sheet.columns)

    def rows(self) -> list[str]:
        return list(self.sheet.index.values)

    def date_columns(self) -> list[str]:
        return [c for c in self.sheet.columns if re.match('\d{2}-\d{2}-\d{2}', c.replace('/', '-')) is not None]

    def to_series(self, metric: str) -> pd.Series:
        return pd.Series(self.sheet.loc[metric, self.date_columns()].values,
                         index=standardize_date(list(self.date_columns())))


def load_sheets(sheet_title: str, credentials: str) -> dict[str, Sheet]:

    gc = gspread.service_account(credentials)
    sheet = gc.open(sheet_title)

    all_sheets = {}
    for wsh in sheet.worksheets():
        all_sheets[wsh.title] = Sheet(wsh.get_all_records())

    return all_sheets

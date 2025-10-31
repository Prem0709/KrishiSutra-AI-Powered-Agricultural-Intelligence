import pandas as pd
import json, os, zipfile, io, pyarrow.parquet as pq

def load_data(file_path):
    """
    Automatically loads CSV, Excel, JSON, Parquet, or ZIP (containing any of these)
    Returns a pandas DataFrame
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(file_path)

    elif ext in [".xls", ".xlsx"]:
        # Combine all sheets into one DataFrame
        xls = pd.ExcelFile(file_path)
        df = pd.concat([xls.parse(sheet) for sheet in xls.sheet_names], ignore_index=True)

    elif ext == ".json":
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Convert list/dict to DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and "records" in data:
            df = pd.DataFrame(data["records"])
        else:
            df = pd.json_normalize(data)

    elif ext == ".parquet":
        df = pq.read_table(file_path).to_pandas()

    elif ext == ".zip":
        dfs = []
        with zipfile.ZipFile(file_path, 'r') as z:
            for name in z.namelist():
                if name.endswith(('.csv', '.xlsx', '.json', '.parquet')):
                    with z.open(name) as f:
                        inner_ext = os.path.splitext(name)[1].lower()
                        # read according to inner type
                        if inner_ext == '.csv':
                            dfs.append(pd.read_csv(f))
                        elif inner_ext in ['.xls', '.xlsx']:
                            dfs.append(pd.read_excel(f))
                        elif inner_ext == '.json':
                            dfs.append(pd.read_json(f))
                        elif inner_ext == '.parquet':
                            dfs.append(pq.read_table(f).to_pandas())
        df = pd.concat(dfs, ignore_index=True)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Clean up column names
    df.columns = df.columns.str.strip().str.replace('\n', '_').str.replace(' ', '_')
    return df

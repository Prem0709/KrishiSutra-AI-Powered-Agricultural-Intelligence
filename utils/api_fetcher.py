import requests
import pandas as pd
import xml.etree.ElementTree as ET

def fetch_data_gov_api(api_key, resource_id, format="json", limit=100):
    url = f"https://api.data.gov.in/resource/{resource_id}?api-key={api_key}&format={format}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("API request failed")

    if format == "json":
        data = response.json()
        return pd.DataFrame(data["records"])

    elif format == "xml":
        root = ET.fromstring(response.content)
        records = []
        for item in root.findall(".//item"):
            record = {child.tag: child.text for child in item}
            records.append(record)
        return pd.DataFrame(records)

    else:
        raise ValueError("Unsupported API format")

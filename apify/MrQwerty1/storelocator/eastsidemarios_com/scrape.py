import csv

from concurrent import futures
from datetime import datetime
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )

        for row in data:
            writer.writerow(row)


def get_ids():
    ids = []
    r = session.get(
        "https://iosapi.eastsidemarios.com/CaraAPI/APIService/getStoreList?from=90.000,-180.000&to=-90.000,180.000&eCommOnly=N",
        headers=headers,
    )
    js = r.json()["response"]["responseContent"]["storeModel"]
    for j in js:
        ids.append(j["storeNumber"])

    return ids


def get_data(_id):
    locator_domain = "https://www.eastsidemarios.com"
    api = f"https://iosapi.eastsidemarios.com/CaraAPI/APIService/getStoreDetails?storeNumber={_id}&numberOfStoreHours=7"
    page_url = f"https://www.eastsidemarios.com/en/locations/{_id}/.html"

    r = session.get(api, headers=headers)
    j = r.json()["response"]["responseContent"]

    location_name = j.get("storeName")
    street_address = f'{j.get("streetNumber")} {j.get("street")}'
    city = j.get("city") or "<MISSING>"
    state = j.get("province") or "<MISSING>"
    postal = j.get("postalCode") or "<MISSING>"
    country_code = "CA"
    store_number = _id
    phone = j.get("phoneNumber") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = j.get("hours") or []
    for d in days:
        s = d.get("store") or {}
        isaval = s.get("available")
        if not isaval:
            continue

        day = datetime.strptime(d.get("date"), "%Y-%m-%d").strftime("%A")
        start = s.get("open")
        end = s.get("close")
        _tmp.append(f"{day}: {start} - {end}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    row = [
        locator_domain,
        page_url,
        location_name,
        street_address,
        city,
        state,
        postal,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]

    return row


def fetch_data():
    out = []
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://www.eastsidemarios.com",
        "Connection": "keep-alive",
        "Referer": "https://www.eastsidemarios.com/",
    }
    scrape()

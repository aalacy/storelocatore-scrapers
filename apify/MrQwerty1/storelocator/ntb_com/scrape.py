import csv

from concurrent import futures
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
    session = SgRequests()
    r = session.get(
        "https://www.ntb.com/rest/model/com/tbc/store/StoreLocatorService/getAllActiveStores"
    )
    js = r.json()["output"]["storeDetailList"]
    for j in js:
        ids.append(j.split(" - ")[0])

    return ids


def get_data(_id):
    locator_domain = "https://www.ntb.com/"
    api_url = f"https://www.ntb.com/rest/model/com/tbc/store/StoreLocatorService/getStoreDetailsByID?q=14b325be2f576b8fef21f4c6e3c8b6d9&storeID={_id}"

    session = SgRequests()
    r = session.get(api_url)
    j = r.json()["output"]["store"]

    # some of pages are broken
    if not j:
        return

    page_url = f"https://www.ntb.com/store/{_id}/"
    a = j.get("address", {})
    location_name = a.get("address1") or "<MISSING>"
    street_address = (
        f"{a.get('address1')} {a.get('address2') or ''}".strip() or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("zipcode") or "<MISSING>"
    country_code = "US"
    store_number = _id
    phone = j.get("phoneNumbers", ["<MISSING>"])[0]
    m = j.get("mapCenter", {})
    latitude = m.get("latitude") or "<MISSING>"
    longitude = m.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("workingHours")
    for h in hours:
        day = h.get("day")
        start = h.get("openingHour")
        close = h.get("closingHour")

        if start == "Closed":
            _tmp.append(f"{day}: Closed")
        else:
            _tmp.append(f"{day}: {start}-{close}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        return

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

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
    scrape()

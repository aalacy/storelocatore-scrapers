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
    r = session.get("https://www.dior.com/store/json/posG.json")
    js = r.json()["items"]
    for j in js:
        country = j[4]
        if country == "US" or country == "CA":
            ids.append(j[0])

    return ids


def generate_urls(ids):
    urls = []
    u = "https://tpc33of0na.execute-api.eu-west-1.amazonaws.com/prod/PointOfSale?ids="
    _tmp = []
    cnt = 0
    for i in ids:
        if cnt == 100:
            urls.append(f'{u}{",".join(_tmp)}')
            _tmp = []
            cnt = 0
        _tmp.append(i)
        cnt += 1

    urls.append(f'{u}{",".join(_tmp)}')
    return urls


def get_data(url):
    rows = []
    locator_domain = "https://www.dior.com/"

    session = SgRequests()
    r = session.get(url)
    js = r.json()["Items"]

    for j in js:
        page_url = "<MISSING>"
        location_name = j.get("defaultName").strip()
        street_address = (
            f"{j.get('defaultStreet1')} {j.get('defaultStreet2') or ''}".strip()
            or "<MISSING>"
        )
        street_address = " ".join(street_address.split())
        city = j.get("defaultCity") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("defaultZipCode", "").strip() or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"

        if len(postal) > 5 and country_code == "US":
            state = postal.split()[0]
            postal = postal.split()[1]

        if len(postal) > 7 and country_code == "CA":
            state = postal.split()[0]
            postal = postal.replace(state, "").strip()

        store_number = "<MISSING>"
        phone = j.get("phoneNumber") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("calculatedWeeklyOpeningHours") or []

        for h in hours:
            index = h.get("day")
            day = days[int(index)]

            t = h.get("hours")
            if t:
                start = t[0].get("from")
                close = t[0].get("to")
            else:
                start, close = "", ""

            if start and start != close:
                _tmp.append(f"{day}: {start} - {close}")
            else:
                _tmp.append(f"{day}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    ids = get_ids()
    urls = generate_urls(ids)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                if row:
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

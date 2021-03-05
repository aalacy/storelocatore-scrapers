import csv
import json

from concurrent import futures
from lxml import html
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


def get_exclude_list(st):
    session = SgRequests()
    r = session.get(f"https://stores.orschelnfarmhome.com/results/?state={st}")
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//input[@id='locationsToExclude']/@value")).split(",")


def get_data(st):
    rows = []
    ex = get_exclude_list(st)
    locator_domain = "https://stores.orschelnfarmhome.com"
    api_url = f"https://stores.orschelnfarmhome.com/umbraco/api/Location/GetDataByState?region={st}"

    session = SgRequests()
    r = session.get(api_url)
    js = json.loads(r.json())["StoreLocations"]

    for j in js:
        _id = j.get("LocationNumber")
        if _id in ex:
            continue
        name = j.get("Name").strip()
        e = j.get("ExtraData", {}) or {}
        a = e.get("Address", {}) or {}
        street_address = (
            f"{a.get('AddressNonStruct_Line1')} {a.get('AddressNonStruct_Line2') or ''}".strip()
            or "<MISSING>"
        )
        city = a.get("Locality") or "<MISSING>"
        state = a.get("Region") or "<MISSING>"
        postal = a.get("PostalCode") or "<MISSING>"
        country_code = a.get("CountryCode") or "<MISSING>"
        store_number = e.get("ReferenceCode") or "<MISSING>"
        page_url = f"https://stores.orschelnfarmhome.com/{state}/{city}/{store_number}/"
        location_name = f"{name} in {city}, {state}, {postal}"
        phone = e.get("Phone") or "<MISSING>"
        coord = j.get("Location", {}).get("coordinates") or ["<MISSING>", "<MISSING>"]
        latitude = coord[1]
        longitude = coord[0]
        location_type = "<MISSING>"

        _tmp = []
        i = 0
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = e.get("HoursOfOperations", "").split("|") or []
        for d in days:
            _tmp.append(f"{d}: {hours[i]}")
            i += 1

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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, state): state for state in states}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

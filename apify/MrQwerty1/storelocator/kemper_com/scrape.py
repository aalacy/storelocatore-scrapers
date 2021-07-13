import csv

from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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


def get_data(param):
    rows = []
    locator_domain = "https://www.kemper.com/"
    page_url = "<MISSING>"
    headers = {"Content-Type": "application/json"}
    data = (
        '{"radius":50,"address":"","city":"","state":"","zip":"'
        + param
        + '","lineOfBusinessList":["AUTOP","AUTOB","HOME","RENTER","CONDO"]}'
    )

    session = SgRequests()
    r = session.post(
        "https://customer.kemper.com/faa/v1/agency/ka", headers=headers, data=data
    )
    js = r.json()["businessUnitList"][0]["agencyList"]

    for j in js:
        location_name = " ".join(j.get("name").split())
        street_address = (
            f'{j.get("addressLine1")} {j.get("addressLine2") or ""}'.strip()
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
    s = set()
    postals = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, postal): postal for postal in postals
        }
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                check = tuple(row[2:7])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

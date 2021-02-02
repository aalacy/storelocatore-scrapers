import csv
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


def fetch_data():
    out = []
    locator_domain = "https://www2.hm.com/"
    api_url = "https://api.storelocator.hmgroup.tech/v2/brand/hm/stores/locale/en_GB/country/GB?_type=json&openinghours=true"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('streetName1')} {a.get('streetName2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("postCode") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        store_number = j.get("storeCode") or "<MISSING>"
        page_url = "https://www2.hm.com/en_gb/customer-service/shopping-at-hm/store-locator.html"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("openingHours") or []

        for h in hours:
            day = h.get("name")
            start = h.get("opens")
            close = h.get("closes")
            _tmp.append(f"{day}: {start} - {close}")

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

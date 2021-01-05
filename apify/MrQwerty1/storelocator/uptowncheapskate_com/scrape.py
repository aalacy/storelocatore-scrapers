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
    locator_domain = "https://uptowncheapskate.com/"
    api_url = "https://uptowncheapskate.com/global/gen/model/search?include_classes=sitefile%2Caddress&take=6000&location_group_ids=1&country=US&class_string=location"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]["models"]

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('street_1')} {a.get('street_2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zipcode") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        store_number = j.get("location_id") or "<MISSING>"
        page_url = f'https://uptowncheapskate.com{j.get("url_relative")}'
        location_name = j.get("name")
        phone = j.get("c_phone") or "<MISSING>"
        latitude = a.get("latitude") or "<MISSING>"
        longitude = a.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("c_store-hours", "").split("\n")
        days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        for h in hours:
            for d in days:
                if h.find(d) != -1:
                    _tmp.append(h)
                    break

        if "".join(hours).lower().find("coming soon") != -1:
            _tmp = ["Coming Soon"]

        hours_of_operation = ";".join(_tmp) or "Coming Soon"

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

import csv

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


def get_coords(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    lat = "".join(tree.xpath("//meta[@property='latitude']/@content")) or "<MISSING>"
    lng = "".join(tree.xpath("//meta[@property='longitude']/@content")) or "<MISSING>"
    return lat, lng


def fetch_data():
    out = []
    locator_domain = "https://lucillesbbq.com/"
    api_url = "https://lucillesbbq.com/data/locations?_format=json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = (
            f"{j.get('address_1')} {j.get('address_2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zipcode") or "<MISSING>"
        country_code = "US"
        store_number = j.get("fishbowl_id") or "<MISSING>"
        page_url = f'https://lucillesbbq.com/locations/{j.get("url_name")}'
        location_name = j.get("name")
        phone = j.get("phone_number") or "<MISSING>"
        latitude, longitude = get_coords(page_url)
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for d in days:
            time = j.get(f"field_{d}")
            _tmp.append(f"{d.capitalize()}: {time}")

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

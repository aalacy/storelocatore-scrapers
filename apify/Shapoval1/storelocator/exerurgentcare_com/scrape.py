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


def get_data():
    rows = []
    locator_domain = "https://www.fieldandstreamshop.com/"
    api_url = "https://exerurgentcare.com/wp-admin/admin-ajax.php?action=store_search&lat=34.07362&lng=-118.40036&max_results=50&search_radius=10000&filter=12&autoload=1"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("store")
        phone = j.get("phone")
        page_url = j.get("url")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours = j.get("hours")
        block = html.fromstring(hours)
        tmp = []
        days = block.xpath("//table/tr/td/text()")
        time = block.xpath("//table/tr/td/time/text()")
        for d, t in zip(days, time):
            tmp.append(f"{d.strip()}: {t.strip()}")
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

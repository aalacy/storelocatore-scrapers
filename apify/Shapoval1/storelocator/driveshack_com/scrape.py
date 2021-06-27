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


def fetch_data():
    out = []

    locator_domain = "https://www.driveshack.com"
    api_url = "https://www.driveshack.com/page-data/events/orlando/book-a-2-bay-package/page-data.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["result"]["data"]["allContentfulDriveShackLocations"]["edges"]
    for j in js:
        a = j.get("node")
        slug = a.get("slug")
        page_url = f"https://www.driveshack.com/locations/{slug}"

        location_type = "<MISSING>"
        street_address = a.get("address1")
        phone = "<MISSING>"
        state = a.get("state")
        postal = a.get("zipCode")
        country_code = "USA"
        city = a.get("city")
        store_number = "<MISSING>"
        latitude = a.get("locationCoordinates").get("lat")
        longitude = a.get("locationCoordinates").get("lon")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        _tmp = []
        days = tree.xpath(
            '//h4[text()="Hours"]/following-sibling::div[1]/div[1]/div/text()'
        )
        times = tree.xpath(
            '//h4[text()="Hours"]/following-sibling::div[1]/div[2]/div/text()'
        )
        for d, t in zip(days, times):
            _tmp.append(f"{d.strip()}: {t.strip()}")
        hours_of_operation = "; ".join(_tmp) or "<MISSING>"

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

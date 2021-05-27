import csv
import yaml

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
    locator_domain = "https://gymvmt.com"
    api_url = "https://gymvmt.com/clubs/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var allLocations =')]/text()")
    )
    text = text.replace("var allLocations =", "").replace("\t", "").replace(";", "")
    js = yaml.load(text, Loader=yaml.Loader)

    for j in js:
        location_name = j.get("name")
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("id") or "<MISSING>"
        slug = j.get("club")
        page_url = f"{locator_domain}{slug}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        source = j.get("hours") or "<html></html>"
        root = html.fromstring(source)
        hours = " ".join("".join(root.xpath("//text()")).split()).replace("pm ", "pm; ")
        if "Holiday" in hours:
            hours = hours.split("Holiday")[0].strip()

        hours_of_operation = hours or "<MISSING>"

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

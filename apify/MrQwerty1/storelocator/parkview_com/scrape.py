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
    url = "https://www.parkview.com/"
    api_url = "https://www.parkview.com/_services/LocationsService.asmx/GetLocations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    js = tree.xpath("//location")

    for j in js:
        locator_domain = url
        location_name = "".join(j.xpath("./name/text()")) or "<MISSING>"
        street_address = (
            f"{''.join(j.xpath('./address1/text()'))} {''.join(j.xpath('./address2/text()')) or ''}".strip()
            or "<MISSING>"
        )
        city = "".join(j.xpath("./city/text()")) or "<MISSING>"
        state = "".join(j.xpath("./state/text()")) or "<MISSING>"
        postal = "".join(j.xpath("./zip/text()")) or "<MISSING>"
        country_code = "US"
        store_number = "".join(j.xpath("./id/text()")) or "<MISSING>"
        page_url = f"https://www.parkview.com/locations/location-details?location={store_number}"
        phone = "".join(j.xpath("./phone/text()")) or "<MISSING>"
        latitude = "".join(j.xpath("./latitude/text()")) or "<MISSING>"
        longitude = "".join(j.xpath("./longitude/text()")) or "<MISSING>"
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

        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

import csv
import cloudscraper

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

    locator_domain = "https://www.lmcu.org"
    session = SgRequests()

    url = "https://www.lmcu.org/locations/branch-listing"

    scraper = cloudscraper.create_scraper(sess=session)
    r = scraper.get(url).text

    tree = html.fromstring(r)
    tr = tree.xpath("//table//tr[./td[@data-title]]")
    for t in tr:
        page_url = "https://www.lmcu.org/locations/branch-listing"
        location_name = (
            "".join(t.xpath('.//div[@class="contact-name"]//text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "Branch"
        street_address = (
            "".join(t.xpath('.//div[@class="branch-address"]/a/text()[1]'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(t.xpath('.//div[@class="branch-address"]/a/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(t.xpath('.//div[@class="branch-phone"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(t.xpath('.//div[@class="branch-hour"]/div//text()'))
            .replace("\n", "")
            .strip()
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"

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

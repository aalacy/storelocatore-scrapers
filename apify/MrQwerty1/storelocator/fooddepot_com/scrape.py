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
    locator_domain = "https://www.fooddepot.com/"
    api_url = "https://www.fooddepot.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//div[@class='store-list-row-container store-bucket filter-rows']")

    for l in li:
        location_name = "".join(
            l.xpath(".//a[contains(@class, 'store-name')]/text()")
        ).strip()
        lines = l.xpath(".//div[@class='store-address']/text()")
        lines = list(filter(None, [line.strip() for line in lines]))
        street_address = ", ".join(lines[:-1])
        line = lines[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        try:
            store_number = location_name.split("#")[1].strip().split()[0]
        except IndexError:
            store_number = "<MISSING>"

        slug = "".join(l.xpath(".//a[contains(text(), 'Store Details')]/@href")) or ""
        page_url = f"https://www.fooddepot.com{slug}"
        phone = (
            "".join(l.xpath(".//a[@class='store-phone']/text()")).strip() or "<MISSING>"
        )

        try:
            text = "".join(
                l.xpath(".//a[@class='block-link' and contains(@href, 'google')]/@href")
            )
            latitude, longitude = text.split("/")[-1].split(",")
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(
                l.xpath(".//div[@class='store-list-row-item-col02']/text()")
            ).strip()
            or "<MISSING>"
        )

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

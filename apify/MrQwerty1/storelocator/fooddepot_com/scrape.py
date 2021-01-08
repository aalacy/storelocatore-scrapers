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
    api_url = "https://www.fooddepot.com/stores/store-search-results.html?zipcode=75022&radius=5000&displayCount=5000"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@data-storeid]")

    for l in li:
        location_name = "".join(
            l.xpath(".//h2[@class='store-display-name h6']/text()")
        ).strip()
        street_address = (
            "".join(l.xpath(".//p[@class='store-address']/text()")).strip()
            or "<MISSING>"
        )
        line = "".join(l.xpath(".//p[@class='store-city-state-zip']/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        country_code = "US"
        if location_name.find("-") != -1:
            store_number = location_name.split("-")[0].strip().split()[-1]
        else:
            store_number = location_name.split("#")[1].strip().split()[0]
        slug = "".join(l.xpath(".//a[@class='store-detail']/@href")) or ""
        page_url = f"https://www.fooddepot.com{slug}"
        phone = (
            "".join(l.xpath(".//p[@class='store-main-phone']/span/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(l.xpath("./@data-storelat")) or "<MISSING>"
        longitude = "".join(l.xpath("./@data-storelng")) or "<MISSING>"
        location_type = "<MISSING>"
        hours = (
            "".join(l.xpath(".//ul[@class='store-regular-hours']/li[2]/text()"))
            .replace(", 7 days a week", "")
            .strip()
        )
        hours_of_operation = f"Mon-Sun: {hours}"

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

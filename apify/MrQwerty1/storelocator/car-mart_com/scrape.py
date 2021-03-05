import cloudscraper
import csv

from lxml import html


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
    locator_domain = "https://www.car-mart.com/"
    api_url = "https://www.car-mart.com/locations/?search=75022&distance=5000"

    scraper = cloudscraper.create_scraper()
    r = scraper.get(api_url)
    tree = html.fromstring(r.text)
    locs = tree.xpath("//div[@class='locations']/div[@class='loc']")

    for l in locs:
        location_name = "".join(l.xpath(".//h2/a/text()")).strip()
        slug = "".join(l.xpath(".//h2/a/@href"))
        line = l.xpath(".//div[@class='info']/p[1]//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        country_code = "US"
        store_number = slug.split("-")[-1].replace("/", "")
        page_url = f"https://www.car-mart.com{slug}"
        phone = "".join(l.xpath(".//a[contains(@href, 'tel')]/text()")) or "<MISSING>"
        latitude = "".join(l.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(l.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(l.xpath(".//p[contains(text(), 'Hours')]/text()"))
            .replace("Hours", "")
            .strip()
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

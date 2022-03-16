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
    locator_domain = "https://baileysgym.com/"
    api = "https://baileysgym.com/page/Locations.aspx"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-list' and ./div/a]")

    for d in divs:
        location_name = "".join(d.xpath("./div/a[1]/text()")).strip()
        slug = "".join(d.xpath("./div/a[1]/@href"))
        page_url = f"https://baileysgym.com{slug}"

        line = d.xpath(
            ".//div[contains(text(), 'Address')]/following-sibling::div[1]//text()|.//strong[.//span[contains(text(), 'Address')]]/following-sibling::div[1]//text()"
        )
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    ".//div[contains(text(), 'Phone')]/following-sibling::div[1]/strong/text()|.//div[contains(text(), 'Phone')]/following-sibling::div[1]/text()"
                )
            ).strip()
            or "<MISSING>"
        )
        if "TBA" in phone:
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if "coming" in location_name.lower():
            hours_of_operation = "Coming Soon"

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

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


def get_hours(page_url):
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    hours_of_operation = (
        "".join(
            tree.xpath("//span[./span[text()='Hours:']]/following-sibling::text()[1]")
        ).strip()
        or "<MISSING>"
    )

    if "(" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("(")[0].strip()

    return hours_of_operation


def fetch_data():
    out = []
    locator_domain = "https://www.sparklemarkets.com/"
    api_url = "https://www.sparklemarkets.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@role='gridcell']")

    for d in divs:
        location_name = "".join(d.xpath(".//div/h4/text()")).strip()
        line = d.xpath(".//div[./h4]/following-sibling::div[1]/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line.pop(0)
        city = "".join(line).split(",")[0].strip()
        line = "".join(line).split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(d.xpath(".//a[./span[text()='Details']]/@href"))
        phone = "".join(
            d.xpath(".//div[./h4]/following-sibling::div[1]/p/span//text()")
        ).strip()
        latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        if "spark" in page_url:
            hours_of_operation = get_hours(page_url)
        else:
            hours_of_operation = "<MISSING>"
            page_url = api_url

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

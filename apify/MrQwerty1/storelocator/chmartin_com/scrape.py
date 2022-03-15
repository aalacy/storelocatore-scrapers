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
    locator_domain = "https://chmartin.com/"
    api = "https://chmartin.com/aboutus.html"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@id, 'e') and ./span/a[contains(@href, 'store')]]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//a//text()")).strip()
        slug = "".join(d.xpath(".//a/@href"))
        page_url = f"{locator_domain}{slug}"
        line = d.xpath(".//font[@size='3']//text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = line.pop().replace("Phone:", "").strip()
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = slug.replace("store", "").replace(".html", "")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        hours = d.xpath(".//font[@size='2']//text()")
        hours = list(filter(None, [h.strip() for h in hours]))[1:]
        hours_of_operation = ";".join(hours) or "<MISSING>"

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

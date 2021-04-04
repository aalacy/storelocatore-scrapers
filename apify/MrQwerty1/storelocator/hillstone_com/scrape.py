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
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//table[@class='hours']//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]/text()")).strip()
        time = "".join(t.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours = ";".join(_tmp) or "<MISSING>"
    if hours.lower().find("call") != -1:
        hours = "<MISSING>"
    if hours.lower().find("closed") != -1:
        hours = "Closed"

    return hours


def fetch_data():
    out = []
    locator_domain = "https://hillstone.com/"
    api_url = "https://hillstone.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location clearfix']")

    for d in divs:
        street_address = (
            "".join(d.xpath(".//span[@itemprop='streetAddress']/text()")).strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath(".//span[@itemprop='addressLocality']/text()")).strip()
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath(".//span[@itemprop='addressRegion']/text()")).strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath(".//span[@itemprop='postalCode']/text()")).strip()
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        try:
            page_url = d.xpath(".//a[@itemprop='url']/@href")[-1].strip()
        except IndexError:
            page_url = "<MISSING>"
        location_name = (
            " ".join(
                "".join(d.xpath(".//h3[@class='truncate']//text()"))
                .replace("âs", "'s")
                .split()
            )
            or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//a[@itemprop='telephone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)

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

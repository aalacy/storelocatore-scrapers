import csv
import json

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


def get_key():
    session = SgRequests()
    r = session.get("https://www.conns.com/store-locator")
    tree = html.fromstring(r.text)
    cookies = session.get_session().cookies.get_dict()
    return cookies, tree.xpath("//input[@name='form_key']/@value")[0]


def fetch_data():
    out = []
    locator_domain = "https://www.conns.com/"
    cookies, key = get_key()
    api_url = f"https://www.conns.com/store-locator/search?form_key={key}&search_type=simple&current_page=1&page_size=10&page=1&search=75022&distance=5000"

    session = SgRequests()
    r = session.get(api_url, cookies=cookies)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@data-role='map-item']")

    for l in li:
        location_name = "".join(l.xpath(".//h3/a/text()")).strip() or "<MISSING>"
        page_url = "".join(l.xpath(".//h3/a/@href")) or "<MISSING>"

        line = l.xpath(".//div[@class='address']/span/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(l.xpath(".//div[@class='address']/span/a/text()")) or "<MISSING>"
        )
        text = "".join(l.xpath("./@data-item-map"))
        j = json.loads(text)["item"]
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = (
            ";".join(l.xpath(".//div[@class='store-hours-title']//meta/@content"))
            or "Closed"
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

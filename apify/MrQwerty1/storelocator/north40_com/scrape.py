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


def fetch_data():
    out = []
    locator_domain = "https://north40.com"
    api_url = "https://north40.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)

    coords = dict()
    text = "".join(
        tree.xpath("//script[contains(text(), 'pointofsale.places=')]/text()")
    )
    text = text.split("pointofsale.places=")[1].split(";pointofsale.")[0]
    js = json.loads(text)
    for j in js:
        _id = j.get("id")
        lat = j.get("lat")
        lng = j.get("lng")
        coords[_id] = (lat, lng)

    divs = tree.xpath("//div[@class='place US']")
    for d in divs:
        line = d.xpath("./div/text()")
        line = list(filter(None, [l.strip() for l in line]))[:-1]

        phone = line[-1].split()[-1].replace(".", "-")
        slug = "".join(
            tree.xpath(
                f"//p[./a[contains(text(),'{phone}')]]/preceding-sibling::h4/a/@href"
            )
        )
        if not slug.startswith("/"):
            slug = f"/{slug}"
        page_url = f"{locator_domain}{slug}"

        street_address = line[0]
        line = line[1:-1]
        state = line[-1].replace("United States ", "")
        postal = line[-2].split()[0]
        city = line[-2].replace(postal, "").strip()
        country_code = "US"
        store_number = "".join(d.xpath("./h3/a/@id"))
        location_name = "".join(d.xpath("./h3/a/text()")).strip()
        latitude, longitude = coords[store_number]
        location_type = "<MISSING>"

        hours = d.xpath("./div/p/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
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

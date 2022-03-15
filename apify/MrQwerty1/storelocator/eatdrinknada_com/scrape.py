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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_coords(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))
    lat, lng = get_coords_from_embed(text)

    _tmp = []
    hours = tree.xpath("//h2/following-sibling::p[./u]|//div[./u]")
    for h in hours:
        day = "".join(h.xpath("./u/text()")).strip()
        if not day:
            continue

        time = "".join(h.xpath("./text()")).strip()
        if ", Brunch" in time:
            time = time.split(", Brunch")[0].strip()
        _tmp.append(f"{day}: {time}")
    hoo = ";".join(_tmp) or "<MISSING>"

    return lat, lng, hoo


def fetch_data():
    out = []
    locator_domain = "https://www.eatdrinknada.com/"

    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Organization')]/text()"))
    js = json.loads(text)["subOrganization"]

    for j in js:
        page_url = j.get("url")
        location_name = j.get("name")
        a = j.get("address")
        street_address = a.get("streetAddress")
        city = a.get("addressLocality")
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        country_code = "US"
        store_number = "<MISSING>"
        phone = j.get("telephone")
        latitude, longitude, hours_of_operation = get_coords(page_url)
        location_type = "<MISSING>"

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
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    scrape()

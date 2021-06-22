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
            if row is not None:
                writer.writerow(row)


def clean_phone(text):
    out = []
    if text.find("|") != -1:
        text = text.split("|")[0].strip()

    for t in text:
        if t.isdigit():
            out.append(t)
        if len(out) == 10:
            break

    return "(" + "".join(out[:3]) + ") " + "".join(out[3:6]) + "-" + "".join(out[6:])


def get_urls():
    session = SgRequests()
    r = session.get("https://s3.amazonaws.com/solasitemap/sitemaps/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '/locations/')]/text()")


def get_data(page_url):
    locator_domain = "https://www.solasalonstudios.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'http://www.schema.org')]/text()")
    )
    try:
        text = (
            text.split('"description"')[0]
            + '"address"'
            + text.split('"description"')[1].split('"address"')[1]
        )
        j = json.loads(text)
    except:
        return

    location_name = j.get("name")
    if "(" in location_name:
        location_name = location_name.split("(")[0].strip()
    if "ONLY" in location_name:
        location_name = location_name.split("ONLY")[0].strip()
    location_name = location_name.replace("&amp;", "&").replace("&#39;", "'")
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    if street_address.endswith(","):
        street_address = street_address[:-1]
    street_address = street_address.replace("&amp;", "&")
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    country_code = a.get("addressCountry") or "<MISSING>"
    if len(postal) == 7:
        country_code = "CA"
    store_number = "<MISSING>"
    phone = j.get("telephone") or "<MISSING>"
    phone = clean_phone(phone)
    g = j.get("geo")
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    for url in urls:
        data_stuff = get_data(url)
        out.append(data_stuff)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

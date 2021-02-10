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


def get_hours(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    hours = tree.xpath(
        "//h3[contains(text(), 'Hours')]/following-sibling::p[1]//text()"
    )
    if not hours:
        hours = tree.xpath(
            "//div[@class='small-24 medium-8 contact-info large-9 columns text-center ']/div[@class='adr']/following-sibling::p//text()"
        )
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = ";".join(hours).replace(":;", ":") or "<MISSING>"
    if hoo.startswith("Yes"):
        hoo = ";".join(hoo.split(";")[1:])

    text = "".join(tree.xpath("//p/a[contains(@href, 'map')]/@href"))

    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        elif text.find("@") != -1:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
        else:
            latitude = text.split("dir/")[1].split(",")[0]
            longitude = text.split("dir/")[1].split(",")[1].split("/")[0]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude, hoo, r.url


def fetch_data():
    out = []
    locator_domain = "https://jerrysartarama.com/"
    api_url = "https://www.jerrysretailstores.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), '@vocab')]/text()"))
    js = json.loads(text)["@graph"]

    for j in js:
        a = j.get("address")
        street_address = a.get("streetAddress") or "<MISSING>"
        city = a.get("addressLocality") or "<MISSING>"
        state = a.get("addressRegion") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("url").replace("/store-location", "")
        if page_url.find("greensboro") != -1:
            page_url = "https://www.jerryswholesalestores.com/greensboro-nc/"
        location_name = j.get("name").replace("&#8217;", "'")
        location_type = "<MISSING>"
        phone = a.get("telephone") or "<MISSING>"
        latitude, longitude, hours_of_operation, page_url = get_hours(page_url)

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

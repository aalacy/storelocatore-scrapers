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
    if r.status_code == 410:
        return "<MISSING>"

    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'ExerciseGym')]/text()")
    ).replace("[ , ", "[")
    j = json.loads(text)

    _tmp = []
    hours = j.get("openingHours") or []
    for h in hours:
        h = h.strip()
        if len(h) != 2:
            _tmp.append(h)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

    iscoming = tree.xpath("//span[@class='coming_soon']")
    if iscoming:
        hours_of_operation = "Coming Soon"

    return hours_of_operation


def fetch_data():
    out = []
    locator_domain = "https://titleboxingclub.com/"
    api_url = "https://titleboxingclub.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//ul[@class='maplocationsectionbottom']/li")

    for l in li:
        location_name = "".join(l.xpath(".//h2/text()")).strip()
        street_address = (
            "".join(l.xpath(".//span[@itemprop='streetAddress']/text()")) or "<MISSING>"
        )
        city = (
            "".join(l.xpath(".//span[@itemprop='addressLocality']/text()"))
            or "<MISSING>"
        )
        state = (
            "".join(l.xpath(".//span[@itemprop='addressRegion']/text()")) or "<MISSING>"
        )
        postal = (
            "".join(l.xpath(".//span[@itemprop='postalCode']/text()")) or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(l.xpath("./a/@href")) or "<MISSING>"
        phone = "".join(l.xpath(".//span[@itemprop='telephone']/text()")) or "<MISSING>"
        if phone.lower().find("text") != -1:
            phone = phone.lower().split("text")[-1].replace(":", "").strip()
        latitude = "".join(l.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(l.xpath("./@data-lon")) or "<MISSING>"
        location_type = "<MISSING>"
        try:
            hours_of_operation = get_hours(page_url)
        except:
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

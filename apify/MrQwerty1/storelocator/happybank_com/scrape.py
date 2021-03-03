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
    hours = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    pp = tree.xpath(
        "//h2[contains(text(),'Lobby Hours')]/following-sibling::p[1]/text()|.//p[contains(text(), 'Lobby Hours')]/text()"
    )

    pp = list(filter(None, [p.strip() for p in pp]))
    if not pp:
        pp = tree.xpath("//div[@id='hours']/p[1]/text()")

    for p in pp:
        p = p.strip()
        if p.find("Lobby") != -1:
            continue
        if p.lower().find("drive") != -1:
            break
        hours.append(p)

    return ";".join(hours) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://happybank.com/"
    api_url = "https://happybank.com/Locations?locpage=search"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'JSON.stringify(')]/text()"))
    text = text.split("JSON.stringify(")[1].split("),")[0]
    js = json.loads(text)

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        page_url = f'https://happybank.com/Locations{j.get("web")}'
        store_number = page_url.split("=")[-1]
        location_name = j.get("name")
        phone = (
            j.get("phone")
            .replace("BANK", "")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            or "<MISSING>"
        )
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = j.get("category") or "<MISSING>"
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

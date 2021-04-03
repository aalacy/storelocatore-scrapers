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


def get_hours(url):
    session = SgRequests()
    r = session.get(url)
    tree = html.fromstring(r.text)
    _tmp = []
    hoo = tree.xpath(
        "//div[./h5[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'branch hours')]]//text()"
    )
    if not hoo:
        hoo = tree.xpath("//div[./h5[contains(text(), 'Location Hours')]]//text()")
    for h in hoo:
        if "Extended" in h:
            break
        if not h.strip() or "hours" in h.lower() or "*" in h:
            continue

        _tmp.append(h.strip())

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://cadencebank.com/"
    api_url = "https://cadencebank.com/find-us"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'locations.push(')]/text()"))
    divs = text.split("locations.push(")[1:]

    for d in divs:
        _id = d.split("Id :")[1].split('"')[1]
        location_name = "".join(
            tree.xpath(f"//div[@data-id='{_id}']//h4/text()")
        ).strip()
        slug = "".join(
            tree.xpath(f"//div[@data-id='{_id}']//a[@class='location-link']/@href")
        )
        page_url = f"https://cadencebank.com{slug}"

        street_address = d.split("Address:")[1].split('"')[1]
        city = d.split("City:")[1].split('"')[1]
        state = d.split("State:")[1].split('"')[1]
        postal = d.split("ZipCode:")[1].split('"')[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = d.split("Telephone:")[1].split('"')[1]
        latitude = d.split("Longitude:")[1].split(",")[0].strip()
        longitude = d.split("Latitude:")[1].split("}")[0].strip()
        location_type = (
            "".join(tree.xpath(f"//div[@data-id='{_id}']//div[@class='types']/text()"))
            .replace(" + ", ", ")
            .strip()
        )
        if location_type == "ATM" or not location_type:
            continue

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

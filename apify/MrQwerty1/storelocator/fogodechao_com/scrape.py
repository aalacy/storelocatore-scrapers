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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    check = tree.xpath("//h5[text()='Coming Soon!']")
    if check:
        return "Coming Soon"

    hours = ";".join(
        tree.xpath(
            "//ul[@class='hours__list' and .//p[contains(text(),'Dinner') or contains(text(), 'DINNER')]]//li[contains(@class, 'hours')]/text()"
        )
    ).strip()
    lunch = (
        ";".join(
            tree.xpath(
                "//p[contains(text(),'Lunch')]/following-sibling::ul[1]/li/text()"
            )
        ).strip()
        or ""
    )

    if lunch:
        out = f"{hours};Lunch: {lunch}"
    else:
        out = hours or "<MISSING>"

    return out


def fetch_data():
    out = []
    locator_domain = "https://fogodechao.com/"
    api_url = "https://fogodechao.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'locationsData ')]/text()"))
    text = text.split("locationsData = ")[1][:-1]
    js = json.loads(text).values()

    for j in js:
        street_address = j.get("address1") or "<MISSING>"
        cs = j.get("city_state")
        if not cs:
            continue
        city = cs.split(",")[0].strip()
        state = cs.split(",")[-1].strip()
        postal = j.get("address2").split()[-1]
        if len(state) > 2:
            continue
        country_code = "US"
        store_number = "<MISSING>"
        page_url = f'https://fogodechao.com{j.get("url")}'
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
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

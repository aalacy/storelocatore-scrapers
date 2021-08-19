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


def fetch_data():
    out = []

    locator_domain = "https://ruthschris.com/"
    api_url = "https://www.ruthschris.com/api/restaurants/?version=global"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("Url") or "<MISSING>"
        location_name = j.get("Name") or "<MISSING>"
        location_type = "<MISSING>"
        street_address = (
            f"{j.get('Address1')} {j.get('Address2')}".strip() or "<MISSING>"
        )

        state = j.get("State") or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        country_code = j.get("CountryCode").get("Key") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        if street_address.find("Taichung") != -1:
            street_address = street_address.replace(", Taichung", "")
            city = "Taichung"
        store_number = "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        phone = "".join(j.get("Phone")).replace("\t", "").strip() or "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = tree.xpath(
            '//div[./h3[text()="Dinner"]]//text() | //div[./h3[text()="Lunch"]]//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = tree.xpath('//div[./h3[text()="Takeout"]]//text()')
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"

        permcls = "".join(
            tree.xpath(
                '//span[contains(text(), "Permanently Closed")]/text() | //span[contains(text(), "permanently")]/text()'
            )
        )
        if permcls:
            hours_of_operation = "Permanently Closed"

        tmpcls = "".join(
            tree.xpath('//span[contains(text(), "Temporarily Closed")]/text()')
        )
        if tmpcls:
            hours_of_operation = "Temporarily Closed"
        cls = "".join(tree.xpath('//span[text()="Location Closed "]/text()'))
        if cls:
            hours_of_operation = "Location Closed"

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

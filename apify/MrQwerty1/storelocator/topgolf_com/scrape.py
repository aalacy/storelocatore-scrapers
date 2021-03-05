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
    locator_domain = "https://topgolf.com/"
    api_url = "https://topgolf.com/venue-locations.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city_name") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("ctx_parent", "").upper() or "<MISSING>"
        store_number = "<MISSING>"
        page_url = j.get("site_url") or "<MISSING>"
        location_name = j.get("context_title")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("hours") or "<html></html>"
        tree = html.fromstring(text)
        divs = tree.xpath("//div[contains(@class, 'vi-hours-row')]")
        for d in divs:
            day = "".join(d.xpath("./div/text()")).strip()
            time = "".join(d.xpath(".//span/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        iscoming = j.get("upcoming")
        isclosed = j.get("longtermclose_text")

        if iscoming == "Yes":
            hours_of_operation = "Coming Soon"

        if isclosed.find("CLOSED") != -1:
            hours_of_operation = "Closed"

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

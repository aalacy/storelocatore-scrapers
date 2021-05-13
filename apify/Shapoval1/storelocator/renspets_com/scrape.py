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
    locator_domain = "https://www.renspets.com"
    page_url = "https://www.renspets.com/store_locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    block = "".join(tree.xpath('//div[@class="store-results-map"]/@data-google-map'))
    js = json.loads(block)
    for j in js["locations"]:
        a = j.get("address")
        location_name = "".join(j.get("name"))
        street_address = f"{a.get('street')} {a.get('street_2')}"
        city = a.get("city")
        state = a.get("region")
        country_code = a.get("country")
        postal = a.get("postal_code")
        store_number = "<MISSING>"
        latitude = j.get("coordinates")[1]
        longitude = j.get("coordinates")[0]
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(j.get("description"))
            .replace("<br>", " ")
            .replace("<div> </div>", "")
        )
        phone = a.get("phone_number") or "<MISSING>"
        if location_name.find("COMING SOON") != -1:
            hours_of_operation = "Coming Soon"

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

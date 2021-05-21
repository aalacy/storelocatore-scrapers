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
    locator_domain = "https://www.nmb-t.com/"
    api_url = "https://www.nmb-t.com/locations"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "location-item")]')
    for d in div:

        page_url = "https://www.nmb-t.com/locations"
        location_name = "".join(d.xpath(".//div[2]//h3/text()"))
        street_address = (
            "".join(d.xpath('.//div[@class="thoroughfare"]/text()'))
            + " "
            + "".join(d.xpath('.//div[@class="premise"]/text()'))
        )
        city = "".join(d.xpath('.//span[@class="locality"]/text()'))
        state = "".join(d.xpath('.//span[@class="state"]/text()'))
        country_code = "US"
        postal = "".join(d.xpath('.//span[@class="postal-code"]/text()'))
        store_number = "".join(d.xpath(".//div[1]//h3/text()"))
        ll = "".join(d.xpath('.//div[@class="coordinates"]/text()'))
        js = json.loads(ll)
        latitude = js.get("coordinates")[1]
        longitude = js.get("coordinates")[0]
        location_type = "Branch"
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/b[contains(text(), "Lobby hours:")]/following-sibling::text() | .//b[contains(text(), "Lobby hours:")]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .replace("   ", " ")
            .replace("CT", "")
            .strip()
        )
        phone = "".join(d.xpath(".//div/p[position()>1]/text()"))
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

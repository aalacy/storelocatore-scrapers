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

    locator_domain = "https://www.brickhousetavernandtap.com/"
    api_url = "https://www.brickhousetavernandtap.com/view-all-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))

    js = json.loads(jsblock)

    for j in js["subOrganization"]:
        a = j.get("address")
        page_url = j.get("url")
        location_name = j.get("name")
        location_type = j.get("@type")
        street_address = a.get("streetAddress")
        phone = j.get("telephone")
        state = a.get("addressRegion")
        postal = a.get("postalCode")
        country_code = "US"
        city = a.get("addressLocality")
        store_number = "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ll = "".join(tree.xpath('//div[@class="gmaps"]/@data-gmaps-static-url-mobile'))

        latitude = ll.split("center=")[1].split("%")[0]
        longitude = ll.split("center=")[1].split("%2C")[1].split("&")[0]
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h2[contains(text(), "Hours &")]/following-sibling::p[2]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("Happy") != -1:
            hours_of_operation = hours_of_operation.split("Happy")[0].strip()

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

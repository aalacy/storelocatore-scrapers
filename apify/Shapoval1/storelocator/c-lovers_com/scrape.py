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

    locator_domain = "https://c-lovers.com"

    api_url = "https://c-lovers.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="more-link"]/a')
    for b in block:

        page_url = "".join(b.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        jsblock = (
            "["
            + "".join(tree.xpath('//script[contains(text(), "telephone")]/text()'))
            + "]"
        )
        js = json.loads(jsblock)
        for j in js:
            location_name = j.get("name")

            location_type = j.get("@type")
            street_address = j.get("address").get("streetAddress")
            country_code = "CA"
            phone = j.get("telephone")
            state = j.get("address").get("addressRegion")
            postal = "<MISSING>"
            city = j.get("address").get("addressLocality")
            store_number = "<MISSING>"
            hours_of_operation = (
                " ".join(j.get("openingHours")).replace("[", "").replace("]", "")
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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

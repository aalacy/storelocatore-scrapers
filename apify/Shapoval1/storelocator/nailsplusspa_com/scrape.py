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

    locator_domain = "https://www.nailsplusspa.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get("https://www.nailsplusspa.com/locations", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./div[@data-block-json]]")

    for d in div:

        store_number = "<MISSING>"
        location_name = "".join(
            d.xpath(".//preceding-sibling::div[1]//p[1]/strong/text()")
        ).strip()
        phone = (
            "".join(d.xpath(".//preceding-sibling::div[1]//p[2]/strong/text()"))
            .replace("tel.", "")
            .strip()
        )
        country_code = "US"
        page_url = "https://www.nailsplusspa.com/locations"
        js = "".join(d.xpath(".//div/@data-block-json"))
        js = json.loads(js)
        latitude = js.get("location").get("mapLat")
        longitude = js.get("location").get("mapLng")
        street_address = js.get("location").get("addressLine1")
        location_type = js.get("location").get("addressTitle")
        ad = (
            "".join(js.get("location").get("addressLine2"))
            .replace(",", "")
            .replace("nj", "NJ")
            .replace("NJ", ",NJ")
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        city = ad.split(",")[0].capitalize().strip()
        hours_of_operation = (
            " ".join(d.xpath(".//preceding-sibling::div[1]//p[2]/text()"))
            .replace("\n", "")
            .replace("—", "")
            .strip()
        )
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

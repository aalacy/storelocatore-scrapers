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

    locator_domain = "https://www.fitnessunlimited.net/"
    api_url = "https://www.fitnessunlimited.net/store-hours-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "gmpAllMapsInfo ")]/text()'))
        .split('"markers":')[1]
        .split(',"original_id":"1"')[0]
    )
    js = json.loads(jsblock)

    for j in js:
        page_url = "https://www.fitnessunlimited.net/store-hours-locations/"
        location_name = j.get("title")
        ad = "".join(j.get("address"))
        street_address = ad.split(",")[0].strip()
        phone = "".join(j.get("description")).split(":")[1].split("<")[0].strip()
        state = ad.split(",")[2].split()[0].strip()
        postal = ad.split(",")[2].split()[1].strip()
        country_code = ad.split(",")[3].strip()
        city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        latitude = j.get("coord_x")
        longitude = j.get("coord_y")
        location_type = "GYM"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        hours_of_operation = (
            "".join(tree.xpath('//div[@id="block_widget-2"]/text()[2]'))
            + ""
            + "".join(tree.xpath('//div[@id="block_widget-2"]/text()[3]'))
        )
        hours_of_operation = hours_of_operation.strip()

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

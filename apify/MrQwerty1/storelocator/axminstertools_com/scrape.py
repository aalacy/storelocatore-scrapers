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
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    tr = tree.xpath("//table[@class='table']//tr")
    for t in tr:
        day = "".join(t.xpath("./th/text()")).strip()
        time = "".join(t.xpath("./td/text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.axminstertools.com/"
    api_url = "https://www.axminstertools.com/stores?glCountry=GB&glCurrency=GBP"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var store_data')]/text()"))
    text = text.split("var store_data = ")[1].strip()[:-1]
    js = json.loads(text).values()

    for j in js:
        line = j.get("address")
        if line.find(".") != -1:
            postal = line.split(".")[-1].strip()
            line = line.split(".")[0].split(",")
        else:
            postal = line.split(",")[-1].strip()
            line = line.split(",")[:-1]
        state = line[-1].strip()
        city = line[-2].strip()
        street_address = ", ".join(line[:-2])
        country_code = "GB"
        store_number = "<MISSING>"
        page_url = f'https://www.axminstertools.com{j.get("url")}'
        location_name = j.get("name")
        phone = j.get("phoneNumber") or "<MISSING>"
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

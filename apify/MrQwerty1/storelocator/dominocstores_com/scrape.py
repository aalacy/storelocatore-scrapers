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
    locator_domain = "https://dominocstores.com/"
    api_url = "https://dominocstores.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)

    part = dict()
    markers = tree.xpath("//div[@data-x-element='map_google_marker']/@data-x-params")
    for m in markers:
        j = json.loads(m)
        root = html.fromstring(j.get("content"))
        _id = "".join(root.xpath("./a[1]/text()")).split("#")[-1]
        lat = j.get("lat") or "<MISSING>"
        lng = j.get("lng") or "<MISSING>"
        phone = (
            "".join(root.xpath("./a[contains(@href, 'tel')]/text()")).strip()
            or "<MISSING>"
        )
        hoo = "".join(root.xpath("./text()")).strip()
        part[_id] = {"lat": lat, "lng": lng, "phone": phone, "hoo": hoo}

    divs = tree.xpath("//div[contains(@class, 'x-column x-sm x-1-4')]")[:-1]

    for d in divs:
        location_name = "".join(d.xpath(".//a/text()")).strip()
        page_url = "https://dominocstores.com/locations" + "".join(
            d.xpath(".//a/@href")
        )
        line = d.xpath(".//div/p//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = "".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = location_name.split("#")[-1]
        phone = part[store_number].get("phone")
        latitude = part[store_number].get("lat")
        longitude = part[store_number].get("lng")
        location_type = "<MISSING>"
        hours_of_operation = part[store_number].get("hoo")

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

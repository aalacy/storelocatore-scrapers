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
    locator_domain = "https://pizzaplusinc.com/"
    api_url = "https://pizzaplusinc.com/static/data/locations.xml"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker")

    for m in markers:
        street_address = "".join(m.xpath("./@address")) or "<MISSING>"
        city = "".join(m.xpath("./@city")) or "<MISSING>"
        state = "".join(m.xpath("./@state")) or "<MISSING>"
        postal = "".join(m.xpath("./@postal")) or "<MISSING>"
        country_code = "".join(m.xpath("./@country")) or "<MISSING>"
        store_number = "<MISSING>"
        page_url = "https://pizzaplusinc.com/locations"
        location_name = "".join(m.xpath("./@name"))
        phone = "".join(m.xpath("./@phone")) or "<MISSING>"
        latitude = "".join(m.xpath("./@lat")) or "<MISSING>"
        longitude = "".join(m.xpath("./@lng")) or "<MISSING>"
        location_type = "".join(m.xpath("./@category")) or "<MISSING>"

        _tmp = []
        for i in range(1, 4):
            hours = "".join(m.xpath(f"./@hours{i}"))
            if not hours:
                break
            _tmp.append(hours)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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

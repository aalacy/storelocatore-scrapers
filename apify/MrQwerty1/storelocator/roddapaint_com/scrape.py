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
    session = SgRequests()
    locator_domain = "https://www.roddapaint.com/"

    r = session.get("https://www.roddapaint.com/store-locations")
    tree = html.fromstring(r.text)
    states = tree.xpath("//ul[@class='nav L4 active']/li/a/@href")

    for s in states:
        r = session.get(f"https://www.roddapaint.com{s}")
        tree = html.fromstring(r.text)
        text = (
            "".join(tree.xpath("//script[contains(text(), '<?xml')]/text()"))
            .split('encoding="utf-16"?>')[1]
            .replace("')", "")
        )
        root = html.fromstring(text)
        markers = root.xpath("//marker")

        for m in markers:
            street_address = "".join(m.xpath("./@street")) or "<MISSING>"
            city = "".join(m.xpath("./@city")) or "<MISSING>"
            state = "".join(m.xpath("./@statecode")) or "<MISSING>"
            postal = "".join(m.xpath("./@postalcode")) or "<MISSING>"
            country_code = "".join(m.xpath("./@country")) or "<MISSING>"
            if country_code == "United States":
                country_code = "US"
            store_number = "".join(m.xpath("./@storeid")) or "<MISSING>"
            slug = "".join(m.xpath("./@storeurlname")) or "<MISSING>"
            page_url = f"https://www.roddapaint.com/store-locations/location-detail/{store_number}/{slug}"
            location_name = "".join(m.xpath("./@name")).replace("\\", "")
            phone = "".join(m.xpath("./@phone")) or "<MISSING>"
            latitude = "".join(m.xpath("./@lat")) or "<MISSING>"
            longitude = "".join(m.xpath("./@lng")) or "<MISSING>"
            location_type = "".join(m.xpath("./@category")) or "<MISSING>"

            _tmp = []
            mf = "".join(m.xpath("./@hoursmf"))
            s = "".join(m.xpath("./@hourss"))
            if mf:
                _tmp.append(f"M2F: {mf}")
            if s:
                _tmp.append(f"Sat: {s}")
            if mf and s:
                _tmp.append("Sun: Closed")

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

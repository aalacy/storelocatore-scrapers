import csv
import yaml

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
    locator_domain = "https://mypiada.com/"
    page_url = "https://mypiada.com/locations?l=all"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'var stores = [],')]/text()"))
    text = text.split("var marker;")[1:]

    for t in text:
        j = yaml.load(
            t.split("stores.push(")[1].split(");")[0].replace("\t", ""),
            Loader=yaml.Loader,
        )

        a = j.get("address")
        root = html.fromstring(a)
        line = root.xpath("//text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"

        store_number = j.get("oloID") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone").split(">")[-1].replace("Â", "").strip() or "<MISSING>"
        loc = j.get("geo") or "<MISSING>,<MISSING>"
        latitude, longitude = loc.split(",")
        location_type = "<MISSING>"

        isclosed = j.get("temporarilyClosed")
        if isclosed:
            hours_of_operation = "Closed"
        else:
            hours_of_operation = f"{j.get('openTime')} - {j.get('closeTime')}"

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

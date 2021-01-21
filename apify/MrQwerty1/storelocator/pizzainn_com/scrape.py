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


def get_coords(tree):
    out = {}
    script = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    text = script.split("var locations =")[1].split("];")[0] + "]"
    lines = eval(text)
    i = 0
    for line in lines:
        out[f"{i}"] = ",".join(map(str, line[-3:-1]))
        i += 1

    return out


def fetch_data():
    out = []
    locator_domain = "https://www.pizzainn.com/"
    api_url = "https://www.pizzainn.com/locations/"
    data = {
        "longitude": "-97.12516989999999",
        "latitude": "33.0218117",
        "radius": "10000",
    }

    session = SgRequests()
    r = session.post(api_url, data=data)
    tree = html.fromstring(r.text)

    loc = tree.xpath("//div[@class='row']")
    coords = get_coords(tree)

    i = 0
    for l in loc:
        location_name = "".join(l.xpath(".//h3[@class='loc-name']/a/text()")).strip()
        adr1 = "".join(l.xpath(".//span[@class='loc-address-1']/text()")).strip() or ""
        adr2 = "".join(l.xpath(".//span[@class='loc-address-2']/text()")).strip() or ""

        street_address = f"{adr1} {adr2}".strip() or "<MISSING>"
        line = "".join(l.xpath(".//span[@class='loc-address-3']/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(l.xpath(".//h3[@class='loc-name']/a/@href"))
        phone = (
            "".join(l.xpath(".//span[@class='loc-phone']/text()")).strip()
            or "<MISSING>"
        )
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        latitude, longitude = coords.get(f"{i}", ",").split(",") or (
            "<MISSING>",
            "<MISSING>",
        )
        location_type = "<MISSING>"

        hours_of_operation = (
            ";".join(l.xpath(".//span[@class='loc-hours']/text()")) or "<MISSING>"
        )
        i += 1
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

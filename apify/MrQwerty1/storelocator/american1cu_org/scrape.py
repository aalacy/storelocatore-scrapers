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
    locator_domain = "https://www.american1cu.org/"
    page_url = "https://www.american1cu.org/locations?street=&search=&state=&radius=&options%5B%5D=branches&options%5B%5D=cuatms&options%5B%5D=shared_branches"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    coords = dict()
    text = "".join(
        tree.xpath("//script[contains(text(), 'var point =')]/text()")
    ).split("var point =")[1:-1]
    for t in text:
        ll = eval(t.split("LatLng")[1].split(";")[0])
        _id = t.split(",")[-1].split(")")[0].strip()
        coords[_id] = ll

    divs = tree.xpath("//div[@class='listbox']")
    for d in divs:
        location_name = "".join(
            d.xpath(".//a[contains(@onclick, 'myClick(')]/text()")
        ).strip()
        store_number = (
            "".join(d.xpath(".//a[contains(@onclick, 'myClick(')]/@onclick"))
            .split("(")[1]
            .split(")")[0]
        )

        line = d.xpath(".//*[contains(@class,'icons')]/following-sibling::p[1]/text()")
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"

        try:
            phone = "".join(
                d.xpath(".//p[./strong[contains(text(), 'Phone')]]")[0].xpath(
                    "./text()"
                )
            ).strip()
        except IndexError:
            phone = "<MISSING>"
        latitude, longitude = coords[store_number]

        fill = "".join(d.xpath(".//path/@fill"))
        if fill == "#002D5B":
            location_type = "Branch"
        elif fill == "#AE132A":
            location_type = "ATM"
        elif fill == "#666666":
            location_type = "Shared Branch"
        else:
            location_type = "<MISSING>"

        hours = d.xpath(
            ".//p[./strong[contains(text(), 'Lobby')]]/following-sibling::blockquote[1]/text()|.//p[./strong[contains(text(), 'Branch')]]/following-sibling::blockquote[1]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours_of_operation = ";".join(hours) or "<MISSING>"

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

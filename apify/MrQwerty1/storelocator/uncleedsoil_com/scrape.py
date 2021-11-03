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


def get_hours():
    out = dict()
    session = SgRequests()
    r = session.get("https://www.uncleedsoil.com/Oil-Change-Service-Locations")
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locations-results']")
    for d in divs:
        key = "".join(d.xpath(".//h3[@class='results-location-title']/a/@href")).split(
            "/"
        )[-1]
        _tmp = d.xpath(".//div[@class='results-section third']//li/text()")
        _tmp = list(filter(None, [t.strip() for t in _tmp]))
        out[key] = ";".join(_tmp) or "<MISSING>"

    return out


def fetch_data():
    out = []
    locator_domain = "https://www.uncleedsoil.com/"
    api_url = "https://www.uncleedsoil.com/Desktopmodules/UncleEds.Locations/MapPoints.ashx?zipcode=48906&radius=999"
    hours = get_hours()

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        text = j.get("Description") or "<html></html>"
        tree = html.fromstring(text)
        location_name = "".join(tree.xpath("//h2/a/text()")).strip()
        street_address = j.get("StreetAddress") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = "".join(tree.xpath("//span[@class='popup-postalcode']/text()")).strip()
        country_code = "US"
        store_number = "<MISSING>"
        slug = j.get("VanityURL")
        page_url = f"https://www.uncleedsoil.com/Oil-Change-Service-Location/{slug}"
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = hours.get(slug)

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

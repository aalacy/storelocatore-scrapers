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


def get_hours(page_url):
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    tr = tree.xpath("//div[@id='hours']//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    coords = []
    locator_domain = "https://www.gameworks.com/"
    api = "https://www.gameworks.com/home"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(
        tree.xpath("//script[contains(text(), 'var marker =')]/text()")
    ).split("var marker =")[1:]
    for t in text:
        lat = t.split("lat:")[1].split(",")[0].strip()
        lng = t.split("lng:")[1].split("}")[0].strip()
        coords.append((lat, lng))

    divs = tree.xpath("//ul[@class='location-map-listing']/li")
    for d in divs:
        location_name = "".join(
            d.xpath(".//div[contains(@class,'location-name')]/a/text()")
        ).strip()
        slug = "".join(d.xpath(".//div[contains(@class,'location-name')]/a/@href"))
        page_url = f"https://www.gameworks.com{slug}"

        line = d.xpath(".//div[contains(@class,'location-address')]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//div[contains(@class,'location-phone')]//text()"))
            .replace(" . ", " ")
            .strip()
            or "<MISSING>"
        )
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"
        hours_of_operation = get_hours(page_url)
        if "SOON" in hours_of_operation:
            hours_of_operation = "Coming Soon"

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

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
    locator_domain = "https://hummusandpitas.com/"
    page_url = "https://hummusandpitas.com/Location-THPC-6th-Avenue-NY/Info-Locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'new google.maps.Marker({')]/text()")
    )
    text = text.split("new google.maps.Marker({")[1:]

    for t in text:
        source = f"<html>{t}</html>"
        d = html.fromstring(source)

        location_name = "".join(d.xpath("//div[@class='maptitle']/text()")).strip()
        if location_name == "Union":
            continue

        line = d.xpath("//div[@class='colorTxt']/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[1].replace("-", "").replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath("//span[text()='P:']/following-sibling::span/text()"))
            .replace("|", "")
            .strip()
            or "<MISSING>"
        )
        latitude, longitude = eval(t.split("google.maps.LatLng")[1].split(");")[0])
        location_type = "<MISSING>"

        _tmp = []
        hours = d.xpath("//div[@class='left']|//div[@class='right']")
        for h in hours:
            day = "".join(h.xpath("./div[1]//text()")).strip()
            time = "".join(h.xpath("./div[last()]//text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if phone == "<MISSING>":
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

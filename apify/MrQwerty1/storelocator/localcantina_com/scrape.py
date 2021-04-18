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


def get_coords(_id):
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.localcantina.com/locations",
    }
    r = session.get(
        f"https://www.localcantina.com/locations?m={_id}&getGeometry=true&mch=true",
        headers=headers,
    )
    js = next(iter(r.json().values()))

    return js.get("lat"), js.get("lon")


def fetch_data():
    out = []
    locator_domain = "https://www.localcantina.com/"
    page_url = "https://www.localcantina.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col col-md-4 col-sm-12' and .//a]")

    for d in divs:
        location_name = "".join(
            d.xpath(".//p[@class='bodytext']/strong/text()")
        ).strip()
        store_number = "".join(d.xpath(".//div[@data-url]/@id"))
        latitude, longitude = get_coords(store_number)
        line = d.xpath(
            ".//p[@class='bodytext' and ./strong]/text()|.//p[@class='bodytext' and ./strong]/span/text()"
        )
        line = list(filter(None, [l.replace("Phone:", "").strip() for l in line]))

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        phone = (
            "".join(d.xpath(".//a[@data-global='phone']/text()")).strip() or "<MISSING>"
        )
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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

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
    locator_domain = "https://www.stmtires.biz/"
    api_url = "https://www.stmtires.biz/Locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@id='info']")

    for d in divs:
        location_name = (
            "".join(d.xpath(".//p[@class='subtitle']/strong/text()")).strip()
            or "<MISSING>"
        )

        line = d.xpath(".//div[@class='locationInfo']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        postal = line.split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            "".join(d.xpath(".//p[@class='subtitle']/a/@href")).strip() or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//div[@class='locphone']/a/text()")).strip()
            or "<MISSING>"
        )
        latitude = (
            "".join(d.xpath(".//span[@class='hideDistance distance']/@lat"))
            or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath(".//span[@class='hideDistance distance']/@lon"))
            or "<MISSING>"
        )
        location_type = "<MISSING>"

        _tmp = []
        hours = d.xpath(".//div[@class='locationhours']/text()")
        for h in hours:
            if h.strip():
                h = h.strip()
                if h.find("-") == -1:
                    h += "Closed"
                _tmp.append(h)

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

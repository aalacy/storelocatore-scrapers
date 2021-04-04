import csv
import re

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


def get_phone(url):
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    line = tree.xpath("//p[@class='locdesc']/text()")
    phone = "<MISSING>"
    for l in line:
        if l.find("RETAIL") != -1:
            try:
                phone = re.findall(r"\d{3}-\d{3}-\d{4}", l)[0]
                break
            except IndexError:
                pass
    return phone


def fetch_data():
    out = []
    s = set()
    locator_domain = "https://www.bestonetire.com/"
    api_url = "https://www.bestonetire.com/Locations"
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
    divs = tree.xpath("//div[@class='locwidgetlisting']")

    for d in divs:
        location_name = (
            "".join(d.xpath(".//div[@class='locwidget-name']/a/strong/text()")).strip()
            or "<MISSING>"
        )
        street_address = "".join(
            d.xpath(".//div[@class='locwidget-addr']/text()")
        ).strip()[:-1]
        line = "".join(d.xpath(".//div[@class='locwidget-csz']/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].strip()
        if state.find("-") != -1:
            state = state.split("-")[-1].strip() or "<MISSING>"
        postal = line.split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            "".join(d.xpath(".//div[@class='locwidget-name']/a/@href")) or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//div[@class='locwidget-phone']/a/text()")).strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = get_phone(page_url)
        latitude, longitude = "".join(
            d.xpath(".//div[@class='locwidget-latlong']/text()")
        ).split(",")
        location_type = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"

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
        check = tuple(row[2:6])
        if check not in s:
            s.add(check)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

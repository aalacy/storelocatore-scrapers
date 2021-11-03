import csv

from lxml import html
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.bccannabisstores.com/"
    page_url = "https://www.bccannabisstores.com/pages/store-locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='page--store-locations']")

    for d in divs:
        location_name = (
            "".join(d.xpath(".//h3[@class='store-name']/text()")).strip() or "<MISSING>"
        )
        line = d.xpath(".//div[@class='page--store-locations--store-info']/p//text()")
        line = list(
            filter(
                None,
                [
                    l.replace("Nanaimo", ",Nanaimo").replace("\xa0", " ").strip()
                    for l in line
                ],
            )
        )

        if "Coming" in line[-1]:
            continue
        if "Shop" in line[-1]:
            line.pop()

        line = ", ".join(line).replace(", 9", "9").replace(",,", ",")
        adr = parse_address(International_Parser(), line)
        street_address = (
            f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
                "None", ""
            ).strip()
            or "<MISSING>"
        )
        if "3B Hwy" in line:
            street_address = line.split(",")[0].strip()
        city = adr.city or "<MISSING>"
        state = adr.state or "<MISSING>"
        postal = adr.postcode or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[@class='store-phone']/text()")).strip() or "<MISSING>"
        )
        text = "".join(d.xpath(".//a[contains(@href, 'google')]/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        _tmp = []
        days = d.xpath(".//div[@class='page--store-locations--hours-days']/span/text()")
        times = d.xpath(
            ".//div[@class='page--store-locations--hours-time']/span/text()"
        )

        for da, t in zip(days, times):
            _tmp.append(f"{da.strip()}: {t.strip()}")

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

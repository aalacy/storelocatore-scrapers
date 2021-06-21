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
    s = set()
    locator_domain = "https://www.happybank.com/"
    api = "https://www.happybank.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'locationCard js-location-card') and not(@data-mb-layer='atm')]"
    )

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[@class='locationCard__heading-text']/text()")
        ).strip()
        page_url = "https://www.happybank.com" + "".join(
            d.xpath(".//a[@class='links__primary--large']/@href")
        )
        if "-atm" in page_url or page_url in s:
            continue

        s.add(page_url)
        line = d.xpath(
            ".//div[@class='locationCard__info-text']/a[contains(@href, 'google')]/text()"
        )
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
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        try:
            longitude, latitude = "".join(d.xpath("./@data-mb-coords")).split(",")
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        li = d.xpath(".//li[@class='locationCard__hours-item']")
        for l in li:
            day = "".join(l.xpath("./span/text()")).strip()
            time = "".join(l.xpath("./strong/text()")).strip()
            _tmp.append(f"{day}: {time}")

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

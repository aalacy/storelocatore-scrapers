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
    locator_domain = "https://mybankcnb.com"
    api_url = "https://mybankcnb.com/Connect/Locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://mybankcnb.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    li = tree.xpath('//div[@class="jsonContainer"]')
    for l in li:
        ad1 = "".join(l.xpath('./span[@title="address"]/text()'))
        ad2 = "".join(l.xpath('./span[@title="address2"]/text()'))
        street_address = f"{ad1} {ad2}".strip()
        city = "".join(l.xpath('./span[@title="city"]/text()')).strip()
        postal = "".join(l.xpath('./span[@title="postal"]/text()')).strip()
        state = "".join(l.xpath('./span[@title="state"]/text()')).strip()
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(l.xpath('./span[@title="web"]/a/@href')).strip()
        location_name = "".join(l.xpath('./span[@title="name"]/text()')).strip()
        phone = "".join(l.xpath('./span[@title="phone"]/text()')).strip()
        latitude = "".join(l.xpath('./span[@title="lat"]/text()')).strip()
        longitude = "".join(l.xpath('./span[@title="lng"]/text()')).strip()
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url)
        block = html.fromstring(r.text)
        hours = (
            "".join(
                block.xpath(
                    '//strong[contains(text(), "Lobby")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = hours or "<MISSING>"
        if street_address.find("2813") != -1:
            hours_of_operation = (
                "".join(
                    block.xpath(
                        '//strong[contains(text(), "Lobby")]/following-sibling::text()[2]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if street_address.find("115") != -1:
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

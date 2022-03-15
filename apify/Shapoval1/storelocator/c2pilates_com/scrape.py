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
    locator_domain = "https://www.c2pilates.com"
    page_url = "https://www.c2pilates.com/contact"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath("//p[./span[contains(text(), 'MA')]]")
    for i in block:
        ad = "".join(i.xpath(".//span/text()")).replace(" 7", "7")
        location_name = "".join(i.xpath(".//preceding-sibling::p[2]/span/text()"))
        street_address = "".join(i.xpath(".//preceding-sibling::p[1]/span/text()"))
        if street_address.find("840") != -1:
            location_name = (
                location_name
                + " "
                + "".join(i.xpath(".//preceding-sibling::p[3]/span/text()"))
            )
        phone = "<MISSING>"
        if street_address.find("360") != -1:
            phone = "".join(
                i.xpath('.//following::div/div/span[contains(text(), "-")]/text()')
            )
        city = ad.split(",")[0]
        state = ad.split(",")[1].split()[0]
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if street_address.find("360") != -1:
            latitude = "".join(
                i.xpath(
                    './/preceding::div[@class="u_1581046009 default dmDefaultGradient align-center hasFullWidth inlineMap"]/@data-lat'
                )
            )
            longitude = "".join(
                i.xpath(
                    './/preceding::div[@class="u_1581046009 default dmDefaultGradient align-center hasFullWidth inlineMap"]/@data-lng'
                )
            )
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(i.xpath('.//preceding::dl[@class="open-hours-data"]/div//text()'))
            .replace("\n", "")
            .strip()
        )
        postal = ad.split(",")[1].split()[1]

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

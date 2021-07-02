import csv
from sgrequests import SgRequests
from lxml import html


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


def get_urls():
    urls = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    r = session.get("https://www.acecashexpress.com/locations", headers=headers)
    tree = html.fromstring(r.text)
    states = tree.xpath("//ul[@class='states']/li/a/@href")
    for state in states:
        r = session.get(f"https://www.acecashexpress.com{state}", headers=headers)
        root = html.fromstring(r.text)
        cities = root.xpath("//ul[@class='cities-list']/li/a/@href")
        for city in cities:
            for i in range(1, 5000):
                r = session.get(
                    f"https://www.acecashexpress.com{city}/page/{i}", headers=headers
                )
                tree = html.fromstring(r.text)
                links = tree.xpath(
                    "//ul[@class='stores no-bullet']//p[@class='location']/a/@href"
                )
                for link in links:
                    page_urls = f"https://www.acecashexpress.com{link}"
                    urls.append(page_urls)
                if len(links) < 5:
                    break

    return urls


def get_data():
    out = []
    locator_domain = "https://www.acecashexpress.com/"
    urls = get_urls()
    for page_url in urls:

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
        }
        r = session.get(page_url, headers=headers)
        main = html.fromstring(r.text)
        street_address = "".join(main.xpath('//span[@itemprop="streetAddress"]/text()'))
        state = "".join(main.xpath('//abbr[@itemprop="addressRegion"]/text()'))
        city = "".join(main.xpath('//span[@itemprop="addressLocality"]/text()'))
        postal = "".join(main.xpath('//span[@itemprop="postalCode"]/text()'))
        country_code = "US"
        store_number = "".join(
            main.xpath('//div[@class="row module store-information"]/@data-store')
        )
        location_name = "Store" + " " + store_number
        phone = "".join(
            main.xpath('//div[@id="ace-store"]//a[contains(@href, "tel")]/text()')
        )
        if phone == "() -":
            phone = "<MISSING>"
        latitude = "".join(
            main.xpath('//div[@class="row module store-information"]/@data-latitude')
        )
        if latitude == "0":
            latitude = "<MISSING>"
        longitude = "".join(
            main.xpath('//div[@class="row module store-information"]/@data-longitude')
        )
        if longitude == "0":
            longitude = "<MISSING>"
        location_type = "ACE Cash Express"
        hours_of_operation = (
            " ".join(main.xpath('//ul[@class="hours no-bullet"]/li//text()'))
            .replace("\n", "")
            .strip()
        )

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
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

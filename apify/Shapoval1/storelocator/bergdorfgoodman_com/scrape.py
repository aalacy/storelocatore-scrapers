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
    locator_domain = "https://www.bergdorfgoodman.com"
    api_url = "https://www.bergdorfgoodman.com/stores/index.jsp"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="store-name"]')
    for i in block:

        location_name = "".join(i.xpath(".//a/text()")).replace("\n", "").strip()
        page_url = locator_domain + "".join(i.xpath(".//a/@href"))

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        r = session.get(page_url, headers=headers)
        trees = html.fromstring(r.text)

        street_address = (
            "".join(trees.xpath('//span[@itemprop="streetAddress"]//text()'))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(
            trees.xpath(
                "//h6[contains(text(), 'Phone')]/following-sibling::span/a/text()"
            )
        )
        city = "".join(trees.xpath('//span[@itemprop="addressLocality"]//text()'))
        state = "".join(trees.xpath('//span[@itemprop="addressRegion"]//text()'))
        country_code = "US"
        store_number = "<MISSING>"
        ll = "".join(
            "".join(
                trees.xpath(
                    '//div[@class="phone"]/following-sibling::div[1]/div/a/@href'
                )
            )
            .split("/@")[1]
            .split(",")[:2]
        ).replace("-", ",-")
        latitude = ll.split(",")[0]
        longitude = ll.split(",")[1]
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(trees.xpath("//td/text()"))
            .replace("\n", "")
            .replace("  ", " ")
            .strip()
        )
        postal = "".join(trees.xpath('//span[@itemprop="postalCode"]//text()'))
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

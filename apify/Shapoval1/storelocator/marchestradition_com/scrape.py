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

    locator_domain = "https://www.marchestradition.com/"
    api_url = "https://www.marchestradition.com/en/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store-result "]')
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="store-title"]/@href'))
        location_name = "".join(d.xpath('.//a[@class="store-title"]/span/text()'))
        location_type = "Les Marché Tradition store"
        street_address = (
            "".join(d.xpath('.//span[@class="location_address_address_1"]/text()'))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        state = "".join(d.xpath(".//@data-province")).upper()
        postal = "".join(d.xpath(".//@data-postal-code")).upper()
        country_code = "CA"
        city = "".join(d.xpath(".//@data-city")).capitalize()
        store_number = "".join(d.xpath(".//@data-id"))
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        phone = (
            "".join(d.xpath('.//span[@class="phone"]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            "".join(d.xpath(".//@data-hours"))
            .replace('"', "")
            .replace(":", " ")
            .replace("{", "")
            .replace("}", "")
            .replace(" 00", ":00")
            .replace(" 30", ":30")
            .replace(":00:00", " 00:00")
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
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

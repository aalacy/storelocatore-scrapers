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

    locator_domain = "https://lawtons.ca"
    api_url = "https://lawtons.ca/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[contains(@class, "store-result brand-lawtons-drugs-location")]'
    )
    for d in div:

        page_url = "".join(d.xpath('.//a[@class="store-title"]/@href'))
        location_name = (
            "".join(d.xpath('.//h4[./a[@class="store-title"]]//text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "".join(d.xpath(".//@data-brand"))
        if location_type == "lawtons-drugs-location-with-a-walk-in-clinic":
            continue
        street_address = "".join(
            d.xpath(
                './/p[@class="location_address"]/span[@class="location_address_address_1"]//text()'
            )
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        if phone.find("N/A") != -1:
            phone = "<MISSING>"
        state = (
            "".join(
                d.xpath(
                    './/p[@class="location_address"]/span[@class="province"]//text()'
                )
            )
            or "<MISSING>"
        )
        postal = (
            "".join(
                d.xpath(
                    './/p[@class="location_address"]/span[@class="postal_code"]//text()'
                )
            )
            or "<MISSING>"
        )
        country_code = "CA"
        city = (
            "".join(
                d.xpath('.//p[@class="location_address"]/span[@class="city"]//text()')
            )
            or "<MISSING>"
        )
        store_number = "<MISSING>"
        if page_url.find("charlottetown-") != -1:
            store_number = page_url.split("-")[-1].split("/")[0]

        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        hours_of_operation = (
            "".join(d.xpath(".//@data-hours"))
            .replace("{", "")
            .replace("}", "")
            .replace('"', "")
            .replace("null", "Closed")
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

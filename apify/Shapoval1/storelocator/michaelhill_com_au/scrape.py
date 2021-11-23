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

    locator_domain = "https://www.michaelhill.com.au/"
    api_url = "https://www.michaelhill.com.au/on/demandware.store/Sites-MichaelHillAU-Site/default/StoresHooks-GetStoreList?q=&display=&country=AU&mode=checkstock&lat=-25.274398&lng=133.775136"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store-info"]')

    for d in div:

        page_url = (
            "".join(d.xpath('.//h3[@class="store-name Fnt03 S01"]/a/@href'))
            .replace("\n", "")
            .strip()
        )
        location_name = (
            "".join(d.xpath('.//h3[@class="store-name Fnt03 S01"]/a/text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "Store"
        street_address = (
            "".join(d.xpath('.//span[@class="street-address1"]/text()'))
            .replace("\n", "")
            .strip()
            + " "
            + "".join(d.xpath('.//span[@class="street-address2"]/text()'))
            .replace("\n", "")
            .strip()
        )
        if "closed" in street_address:
            street_address = "<MISSING>"
        if "Closed" in street_address:
            street_address = "<MISSING>"
        phone = (
            "".join(d.xpath('.//span[contains(text(), "Ph:")]/text()'))
            .replace("Ph:", "")
            .strip()
            or "<MISSING>"
        )
        state = (
            "".join(d.xpath('.//span[@class="street-address-state"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        postal = (
            "".join(d.xpath('.//span[@class="postalCode"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        city = (
            "".join(d.xpath('.//span[@class="street-address-city"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        country_code = "AU"
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="store-hours"]//tr//text()'))
            .replace("\n", "")
            .replace("  ", " ")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"
        if hours_of_operation.count("CLOSED") > 7:
            hours_of_operation = "Closed"
        latitude = (
            "".join(d.xpath('.//span[@class="store-lat"]/text()'))
            .replace("\n", "")
            .strip()
        )
        longitude = (
            "".join(d.xpath('.//span[@class="store-lng"]/text()'))
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
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

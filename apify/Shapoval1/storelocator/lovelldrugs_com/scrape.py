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

    locator_domain = "https://lovelldrugs.com"
    page_url = "https://lovelldrugs.com/location"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "storebox ")]')

    for d in div:

        location_name = (
            "".join(d.xpath('.//div[@class="col-xs-12 storetitle"]/text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath('.//div/div[@class="col-xs-3"][1]/div[2]/text()')
        )
        if street_address.find("-") != -1:
            street_address = street_address.split("-")[0].strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()

        state = "<MISSING>"
        postal = "".join(d.xpath('.//div/div[@class="col-xs-3"][1]/div[4]/text()'))
        country_code = "CA"
        city = "".join(d.xpath('.//div/div[@class="col-xs-3"][1]/div[3]/text()'))
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath('.//div[./b[text()="Tel:"]]/text()'))
            .replace("Tel:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[./strong[text()="Store Hours"]]/following-sibling::div//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("temporarily closed") != -1:
            hours_of_operation = "Temporarily Closed"
        if hours_of_operation.find("2021:") != -1:
            hours_of_operation = hours_of_operation.split("2021:")[1].strip()
        if hours_of_operation.find("2020:") != -1:
            hours_of_operation = hours_of_operation.split("2020:")[1].strip()
        if hours_of_operation.find("Hours of Operation:") != -1:
            hours_of_operation = hours_of_operation.split("Hours of Operation:")[
                1
            ].strip()

        url = locator_domain + "".join(d.xpath('.//a[text()="Directions > "]/@href'))
        session = SgRequests()
        r = session.get(url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
            .split("LatLng(")[1]
            .split(",")[0]
            .replace("'", "")
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng(")]/text()'))
            .split("LatLng(")[1]
            .split(",")[1]
            .split(")")[0]
            .replace("'", "")
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

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

    locator_domain = "https://www.conlins.com"
    api_url = "https://www.conlins.com/stores/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.post(api_url, headers=headers)

    tree = html.fromstring(r.text)
    div = tree.xpath("//div[contains(@class, 'store-result store-result')]")

    for d in div:

        page_url = "".join(d.xpath('.//a[@class="store-result__name"]/@href'))
        street_address = "".join(
            d.xpath('.//div[@class="store-result__address__street1"]/text()')
        )
        if street_address.find("1441 Highway 35") != -1:
            continue
        city = "".join(d.xpath('.//span[@class="store-result__address__city"]/text()'))
        state = "".join(
            d.xpath('.//span[@class="store-result__address__state"]/text()')
        )
        postal = "".join(d.xpath('.//span[@class="store-result__address__zip"]/text()'))
        store_number = "<MISSING>"
        location_name = "".join(d.xpath('.//a[@class="store-result__name"]/text()'))

        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lon"))
        country_code = "US"
        location_type = "<MISSING>"
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
            .replace("Call", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="store-result__hours__hours"]/text()'))
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

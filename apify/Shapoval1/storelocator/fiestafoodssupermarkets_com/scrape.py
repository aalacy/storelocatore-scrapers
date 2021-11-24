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

    locator_domain = "https://fiestafoodssupermarkets.com"
    api_url = "https://fiestafoodssupermarkets.com/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="map-multi-marker"]/following::h3[contains(text(), "Store")][position()>3]'
    )
    id = 5
    for d in div:

        page_url = "https://fiestafoodssupermarkets.com/store-locator/"
        location_name = "".join(d.xpath(".//text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//following-sibling::p[1]/text()[1]"))
        ad = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = id
        id += 1
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "markers")]/text()'))
            .split(f'"id":{store_number},')[1]
            .split('"lat":')[1]
            .split(",")[0]
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "markers")]/text()'))
            .split(f'"id":{store_number},')[1]
            .split('"lng":')[1]
            .split(",")[0]
        )
        phone = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[3]"))
            .replace("\n", "")
            .replace("Phone:", "")
            .strip()
        )
        hours_of_operation = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[4]"))
            .replace("\n", "")
            .replace("Hours:", "")
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

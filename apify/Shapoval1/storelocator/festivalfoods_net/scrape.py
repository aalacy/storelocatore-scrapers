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

    locator_domain = "http://festivalfoods.net"
    api_url = "http://festivalfoods.net/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="locationSide"]')

    for d in div:
        page_url = "http://festivalfoods.net" + "".join(
            d.xpath('.//a[contains(text(), "More Info")]/@href')
        )
        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = "<MISSING>"
        street_address = "".join(d.xpath(".//h3/following-sibling::div[1]/text()[1]"))
        ad = (
            "".join(d.xpath(".//h3/following-sibling::div[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        phone = "".join(d.xpath(".//h3/following-sibling::div[2]/a/text()"))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//div[contains(@id, "hours")]/text()'))
            .replace("\n", "")
            .replace("<", "")
            .strip()
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "var glat")]/text()'))
            .split("var glat = '")[1]
            .split("'")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "var glat")]/text()'))
            .split("var glon = '")[1]
            .split("'")[0]
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

import csv
from sgscrape.sgpostal import International_Parser, parse_address
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

    locator_domain = "https://www.santouka.co.jp/en/"
    api_url = "https://www.santouka.co.jp/en/shop-foreign#tab0"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a/div[@class="box"]]')
    for d in div:
        page_url = "".join(d.xpath("./a/@href"))
        location_name = "".join(d.xpath(".//h4/text()"))
        location_type = "<MISSING>"
        ad = (
            "".join(d.xpath('.//p[contains(text(), "Address")]/text()[1]'))
            .replace("Address／", "")
            .replace("/", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        phone = (
            "".join(d.xpath('.//p[contains(text(), "TEL")]/text()'))
            .replace("TEL／", "")
            .strip()
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "".join(d.xpath('.//p[@class="flag"]/span/text()'))
        city = a.city or "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = d.xpath('.//p[contains(text(), "Business Hours")]/text()')
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation)
            .replace("Business Hours／", "")
            .replace("～", "-")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("\r\n", " ")
            .replace("：", ":")
            .replace("  ", " ")
            .replace("　　　 ", " ")
            .strip()
        )
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
            .split("LatLng(")[1]
            .split(",")[0]
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "LatLng")]/text()'))
            .split("LatLng(")[1]
            .split(",")[1]
            .split(")")[0]
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

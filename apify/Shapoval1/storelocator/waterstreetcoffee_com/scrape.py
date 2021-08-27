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

    locator_domain = "https://waterstreetcoffee.com/"
    api_url = "https://waterstreetcoffee.com/cafes/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location--item aligncenter col-xs-12 col-sm-6"]/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        location_type = "<MISSING>"
        street_address = (
            "".join(
                tree.xpath('//span[@class="location-meta--street mb0 blue"]/text()')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(tree.xpath('//span[@class="location-meta--addy mb25 blue"]/text()'))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "".join(
            tree.xpath('//p[@class="location-meta--phone mb5 white"]/text()')
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="location-meta--inner"]/a/preceding-sibling::p//text()'
                )
            )
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

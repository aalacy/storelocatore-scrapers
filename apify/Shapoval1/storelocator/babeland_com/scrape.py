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

    locator_domain = "https://www.babeland.com/"
    api_url = "https://www.babeland.com/content/c/Babeland_Store_Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="shopInfo section group"]')

    for d in div:

        page_url = "https://www.babeland.com/content/c/Babeland_Store_Locations"
        location_name = "".join(d.xpath(".//h3/a/text()"))
        location_type = "<MISSING>"
        street_address = "".join(
            d.xpath(
                './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[1]/li[1]/text()'
            )
        )
        ad = "".join(
            d.xpath(
                './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[1]/li[2]/text()'
            )
        )

        phone = "".join(
            d.xpath(
                './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[2]/li[3]/text()'
            )
        ).strip()
        state = " ".join(ad.split(",")[1].split()[:-1]).strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/div[@class="col-grid span_5_of_12 shopLocation"]/ul[2]/li[2]/text()'
                )
            )
            .replace("\r\n", " ")
            .replace("   ", " ")
            .replace("    ", " ")
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

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

    locator_domain = "https://mattressstoreslosangeles.com"
    api_url = "https://mattressstoreslosangeles.com/pages/visit-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="description"]/a')

    for b in block:
        slug = "".join(b.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        location_name = "".join(b.xpath(".//h2//text()"))
        street_address = "".join(
            b.xpath('.//p[@class="address"]/span[@class="street"]/text()')
        )
        ad = "".join(b.xpath('.//p[@class="address"]/span[@class="city_zip"]/text()'))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = (
            "".join(b.xpath('.//following-sibling::p[@class="phone"]/text()'))
            .replace("\n", "")
            .strip()
        )

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "<MISSING>"
        store_number = "<MISSING>"

        map_link = "".join(
            tree.xpath('//div[@class="embed-container maps"]/iframe/@src')
        )

        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()

        hours_of_operation = tree.xpath('//div[@class="timetable"]//td/text()')
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)

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

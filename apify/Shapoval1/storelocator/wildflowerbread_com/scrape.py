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
    locator_domain = "https://wildflowerbread.com"
    api_url = "https://wildflowerbread.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="eight columns locations"]/div[@class="row"]')
    for b in block:

        street_address = "".join(
            b.xpath('.//span[2][@itemprop="streetAddress"]/text()')
        )
        city = "".join(b.xpath('.//span[@itemprop="addressLocality"]/text()'))
        postal = "".join(b.xpath('.//span[@itemprop="postalCode"]/text()'))
        state = "".join(b.xpath('.//span[@itemprop="addressRegion"]/text()'))
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(b.xpath('.//span[@itemprop="name"]/a/text()'))
        if location_name.find("Airport") != -1:
            street_address = "".join(
                b.xpath('.//span[1][@itemprop="streetAddress"]/text()')
            )
        slug = "".join(b.xpath('.//span[@itemprop="name"]/a/@href'))
        page_url = f"{locator_domain}{slug}"
        phone = "".join(b.xpath('.//a[@itemprop="telephone"]/text()'))
        latln = "".join(b.xpath('.//p[@class="view-more inline"]/a/@href')).split(
            "%40"
        )[1:]
        latln = "".join(latln).replace("%2C", ",")
        if city == "Phoenix":
            session = SgRequests()
            r = session.get(page_url)
            block = r.text.split("var latlng = new google.maps.LatLng(")[1].split(");")[
                0
            ]
            latln = block
        latitude = latln.split(",")[0]
        longitude = latln.split(",")[1]
        location_type = "<MISSING>"
        hours_of_operation = "".join(
            b.xpath('.//span[1][@itemprop="streetAddress"]/text()')
        ).replace("Open ", "")
        if location_name.find("Airport") != -1:
            hours_of_operation = "<MISSING>"
        if location_name.find("Closed") != -1:
            hours_of_operation = "Temporarily closed"
            location_name = location_name.split("-")[1].split("-")[0].strip()

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

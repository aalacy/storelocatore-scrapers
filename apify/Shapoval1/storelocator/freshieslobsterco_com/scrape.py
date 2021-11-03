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


def get_data():
    rows = []
    locator_domain = "https://freshieslobsterco.com/"
    page_url = "https://freshieslobsterco.com/pages/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-block-desc"]')
    for d in div:

        location_name = "".join(d.xpath('.//div[@class="main-heading"]/p/text()'))
        street_address = "".join(
            d.xpath('.//div[@class="location_address"]/p[1]//text()')
        )
        if street_address.find("Be back soon!") != -1:
            continue
        csz = "".join(d.xpath('.//div[@class="location_address"]/p[2]//text()'))
        city = csz.split(",")[0].strip()
        state = csz.split(",")[1].split()[0].strip()
        postal = csz.split(",")[1].split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = "".join(d.xpath('.//div[@class="phone_no"]/p/a/text()'))
        text = "".join(d.xpath(".//p/a[contains(@title, 'google')]/@title"))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = d.xpath('.//div[@class="opentime"]/text()')
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

        rows.append(row)
    return rows


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

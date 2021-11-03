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
    locator_domain = "https://www.mascomabank.com"
    page_url = "https://www.mascomabank.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.content)
    div = tree.xpath('//div[@class="location-overlay"]')
    for j in div:
        ad = j.xpath('.//div[@class="marker"]/text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        street_address = ", ".join(ad[:-1])
        line = ad[-1]
        city = line.split(",")[0]
        line = line.split(",")[1].strip()
        postal = line.split()[-1]
        state = line.replace(postal, "")

        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(j.xpath('.//div[@class="visit"]/a/@href'))
        location_name = "".join(j.xpath('.//div[@class="marker"]/@data-name'))
        phone = "".join(j.xpath('.//div[@class="phone"]/text()'))
        latitude = "".join(j.xpath('.//div[@class="marker"]/@data-lat')) or "<MISSING>"
        longitude = "".join(j.xpath('.//div[@class="marker"]/@data-lng')) or "<MISSING>"
        location_type = "<MISSING>"

        hours = j.xpath('.//div[@class="hours card-header"]/p[1]/strong/text()')
        hours = list(filter(None, [a.strip() for a in hours]))
        hours = "".join(hours)

        hours_of_operation = "Closed"
        if hours == "Lobby Closed":
            hours_of_operation = "Closed"
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

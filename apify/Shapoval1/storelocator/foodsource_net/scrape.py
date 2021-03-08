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
    locator_domain = "http://foodsource.net/"
    page_url = "http://foodsource.net/index.php/locations"
    session = SgRequests()

    r = session.get(page_url)

    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="tr"]/preceding-sibling::div')
    for b in block:
        line = b.xpath('./p/span[@class="location-address"]/text()')
        street_address = "".join(line[0]).strip()
        city = "".join(line[1]).split(",")[0].strip()
        a = "".join(line[1]).split(",")[1].strip()
        state = "".join(a).split()[0]
        postal = "".join(a).split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "<MISSING>"
        phone = "".join(line[4]).replace("\n", "").strip()
        text = "".join(b.xpath('.//span[@class="location-map"]/a/@href'))
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
        hours_of_operation = "".join(line[3]).replace("\n", "").strip()

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

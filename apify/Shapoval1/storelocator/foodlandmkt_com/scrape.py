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

    locator_domain = "https://foodlandmkt.com/"
    page_url = "https://foodlandmkt.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-data"]')

    for d in div:

        title = (
            "".join(d.xpath('.//h3[@class="site-loc-name"]/a/text()'))
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        street_address = "".join(d.xpath('.//div[@class="site-loc-address"]/text()'))
        ad = "".join(d.xpath('.//div[@class="site-city-state-zip"]/text()'))
        phone = (
            "".join(d.xpath('.//div[@class="site-loc-phone"]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "USA"
        city = ad.split(",")[0].strip()
        location_name = title.split("-")[0].strip()
        store_number = title.split("-")[1].replace("(", "").replace(")", "").strip()
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lon"))
        hours_of_operation = (
            "".join(d.xpath('.//div[@class="site-loc-hours"]/text()'))
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

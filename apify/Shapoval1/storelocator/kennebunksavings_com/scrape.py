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
    locator_domain = "https://www.kennebunksavings.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get("https://www.kennebunksavings.com/location/", headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="map-filter__item"]')

    for d in div:

        page_url = "https://www.kennebunksavings.com/location/"
        street_address = "".join(
            d.xpath('.//p[@class="map-filter__item-address"]/span[1]/text()')
        )
        ad = "".join(d.xpath('.//p[@class="map-filter__item-address"]/span[2]/text()'))
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        location_name = "".join(
            d.xpath('. //div[@class="map-filter__control"]/h3/text()')
        )
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "".join(d.xpath('. //div[@class="map-filter__control"]/@data-lat'))
        longitude = "".join(d.xpath('. //div[@class="map-filter__control"]/@data-lng'))
        location_type = "Branch"
        hours_of_operation = d.xpath(
            './/span[@class="map-filter__hours-heading"]/following-sibling::div/div/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation)
        if hours_of_operation.count("Lobby:") == 2:
            hours_of_operation = (
                hours_of_operation.split("Drive Up")[0].replace("Lobby:", "").strip()
            )
        if hours_of_operation.find("Lobby") != -1:
            hours_of_operation = (
                hours_of_operation.split("Lobby:")[1].split("Drive Up")[0].strip()
            )
        if hours_of_operation.find("Drive Up:") != -1:
            hours_of_operation = hours_of_operation.replace("Drive Up:", "").strip()
        hours_of_operation = (
            hours_of_operation.replace("  ", " ").replace("No", "").strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))

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

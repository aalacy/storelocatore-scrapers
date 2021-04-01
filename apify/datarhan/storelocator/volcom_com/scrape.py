import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "volcom.com"
    start_urls = [
        "https://www.volcom.com/blogs/store-locator/tagged/united-states+retail",
        "https://www.volcom.com/blogs/store-locator/tagged/united-states+outlet",
    ]

    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[contains(@class, "StoreLocator__store")]')

        for poi_html in all_locations:
            store_url = poi_html.xpath(".//a[@data-article-tile-image]/@href")
            store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
            location_name = " ".join(
                [elem.strip() for elem in poi_html.xpath(".//h3/text()")]
            )
            if not location_name:
                continue
            raw_address = poi_html.xpath(
                './/p[i[@class="far fa-map-marker-alt"]]/text()'
            )
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]
            if not raw_address:
                continue
            raw_address = raw_address[0].split(", ")
            if len(raw_address) == 5:
                raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
            if "Suit" in raw_address[1]:
                raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
            street_address = raw_address[0]

            if len(raw_address) < 3:
                if len(raw_address[-1].split()) == 2:
                    city = street_address.split()[-1]
                    state = raw_address[-1].split()[0]
                    zip_code = raw_address[-1].split()[-1]
                else:
                    city = raw_address[-1].split()[0]
                    state = raw_address[-1].split()[1]
                    zip_code = raw_address[-1].split()[-1]
            else:
                city = raw_address[1]
                state = raw_address[2].split()[0]
                zip_code = raw_address[2].split()[-1]
            country_code = raw_address[-1]
            if len(country_code.split()[0]) == 2:
                zip_code = country_code.split()[-1]
                state = country_code.split()[0]
                country_code = "United States"
            store_number = "<MISSING>"
            phone = poi_html.xpath(".//div[@data-article-tile-excerpt]/p[2]/text()")
            phone = phone[0].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = poi_html.xpath(
                ".//div[@data-article-tile-excerpt]/p[3]/text()"
            )
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

            if len(city.split()[0]) == 2:
                state = city.split()[0]
                zip_code = city.split()[-1]
                city = " ".join(street_address.split("#")[-1].split()[1:])
                zip_code == "<MISSING>"
            if "Coming Soon" in phone:
                phone = "<MISSING>"
                location_type = "Coming Soon"
            if len(zip_code.strip()) == 2:
                zip_code = "<MISSING>"
            if "United" not in country_code:
                country_code = "<MISSING>"

            item = [
                DOMAIN,
                store_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

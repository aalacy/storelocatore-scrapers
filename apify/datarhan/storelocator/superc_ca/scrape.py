import csv
from lxml import etree

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
    scraped_items = []

    DOMAIN = "superc.ca"
    start_url = "https://www.superc.ca/trouver.fr.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_towns = dom.xpath('//select[@name="town"]/option/@value')

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.superc.ca",
        "referer": "https://www.superc.ca/trouver.fr.html",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    all_locations = []
    for town in all_towns:
        body = "rechercher=1&postalCode1=&postalCode2=&searchMode=town&town={}&method.search=Recherche".format(
            town
        )
        response = session.post(
            "https://www.superc.ca/trouver.fr.html", data=body, headers=headers
        )
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//section[@class="store"]')

    for poi_html in all_locations:
        all_data = poi_html.xpath('.//div[@class="store-infos"]/div/div/p/text()')
        all_data = [elem.strip() for elem in all_data]
        store_url = "<MISSING>"
        location_name = all_data[0]
        street_address = all_data[1]
        city = all_data[2]
        state = poi_html.xpath('.//p[@class="si-info si-link"]/a/@href')[0].split(",+")[
            -2
        ]
        state = state.strip() if state.strip() else "<MISSING>"
        zip_code = all_data[3]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = all_data[-1]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = poi_html.xpath('.//div[@class="store-hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Heures d'ouverture ", "")
            if hours_of_operation
            else "<MISSING>"
        )

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

        check = "{} {}".format(street_address, location_name)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

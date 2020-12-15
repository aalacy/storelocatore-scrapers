import csv
from lxml import etree
from sgrequests import SgRequests
from sgselenium import SgFirefox


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

    DOMAIN = "mobilemini.com"
    start_url = "https://www.mobilemini.com/locations#"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//p[@class="location-text"]/a/@href')
    for url in all_states:
        state_response = session.get("https://www.mobilemini.com" + url)
        state_dom = etree.HTML(state_response.text)
        all_locations += state_dom.xpath(
            '//div[@class="col-md-8 no_padding location-details"]/a[contains(@href, "locations")]/@href'
        )

    for url in list(set(all_locations)):
        store_url = "https://www.mobilemini.com" + url
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@role="article"]//h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@class="address-line1"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@class="locality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@class="administrative-area"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@class="postal-code"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//span[@class="country"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//a[@class="paragraph_link" and contains(@href, "tel")]/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        with SgFirefox() as driver:
            driver.get(store_url)
            driver_r = etree.HTML(driver.page_source)
        latitude = driver_r.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = driver_r.xpath("//@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = loc_dom.xpath('//div[@class="office-hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

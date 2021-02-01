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

    DOMAIN = "brixxpizza.com"
    start_url = "https://brixxpizza.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//a/@data-id")

    for loc_id in all_locations:
        url = "https://brixxpizza.com/wp-content/themes/Brixxpizza/inner-ajax.php"
        formdata = {"id": loc_id}
        loc_response = session.post(url, data=formdata)
        loc_dom = etree.HTML(loc_response.text)

        store_url = loc_dom.xpath('//a[@class="links-red"]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = loc_dom.xpath("//h3/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@data-yext-field="address1"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@data-yext-field="city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@data-yext-field="state"]/text()')
        state = state[0] if state else "<MISSING>"
        state = state.split("-")[-1]
        zip_code = loc_dom.xpath('//span[@data-yext-field="zip"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = loc_id
        phone = loc_dom.xpath('//a[@data-yext-field="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@date-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="frankin-date"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

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

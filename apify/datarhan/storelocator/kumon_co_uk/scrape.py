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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "kumon.co.uk"
    start_url = "https://www.kumon.co.uk/find-a-tutor/"

    all_locations = []

    formdata = {
        "latlon": "0,0",
        "centre_search": "london",
        "chosen_options[1][days_open_monday]": "0",
        "chosen_options[1][days_open_tuesday]": "0",
        "chosen_options[1][days_open_wednesday]": "0",
        "chosen_options[1][days_open_thursday]": "0",
        "chosen_options[1][days_open_friday]": "0",
        "chosen_options[1][days_open_saturday]": "0",
        "chosen_options[1][days_open_sunday]": "0",
        "chosen_options[2][1]": "0",
        "chosen_options[2][2]": "0",
        "chosen_options[3][104]": "0",
        "chosen_options[3][136]": "0",
        "chosen_options[3][138]": "0",
        "widget_search_centres": "",
    }
    hdr = {"Content-Type": "application/x-www-form-urlencoded"}
    response = session.post(start_url, data=formdata, headers=hdr)
    dom = etree.HTML(response.text)

    scraped_urls = []
    all_locations += dom.xpath('//a[contains(@class, "choose-centre-button")]/@href')
    next_page = dom.xpath('//a[small[i[@class="fa fa-chevron-right"]]]/@href')
    while next_page:
        if next_page[0] not in scraped_urls:
            formdata = {
                "centre_search": "london",
                "page": next_page[0].split("=")[-1],
                "chosen_filters": "chosen_options%5B1%5D%5Bdays_open_monday%5D=0&chosen_options%5B1%5D%5Bdays_open_tuesday%5D=0&chosen_options%5B1%5D%5Bdays_open_wednesday%5D=0&chosen_options%5B1%5D%5Bdays_open_thursday%5D=0&chosen_options%5B1%5D%5Bdays_open_friday%5D=0&chosen_options%5B1%5D%5Bdays_open_saturday%5D=0&chosen_options%5B1%5D%5Bdays_open_sunday%5D=0&chosen_options%5B2%5D%5B1%5D=0&chosen_options%5B2%5D%5B2%5D=0&chosen_options%5B3%5D%5B104%5D=0&chosen_options%5B3%5D%5B136%5D=0&chosen_options%5B3%5D%5B138%5D=0",
                "latlon": "0,0",
            }
            response = session.post(start_url, data=formdata, headers=hdr)
            scraped_urls.append(next_page[0])
            dom = etree.HTML(response.text)
            all_locations += dom.xpath(
                '//a[contains(@class, "choose-centre-button")]/@href'
            )
            next_page = dom.xpath('//a[small[i[@class="fa fa-chevron-right"]]]/@href')
            if next_page and next_page[0] in scraped_urls:
                next_page = None

    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="text-center"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')[0]
        street_address += loc_dom.xpath(
            '//span[@itemprop="streetAddress"]/following::text()'
        )[0]
        street_address = street_address if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@class="number"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//table[@class="centre-timings"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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

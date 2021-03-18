import csv
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

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
    session = SgRequests().requests_retry_session(retries=3, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "allinahealth.org"
    start_url = "https://account.allinahealth.org/find/locationsearchby"
    page_url = "https://account.allinahealth.org/find/locationsearchby?PageIndex=1&IsPaging=true&SearchType=zip&FilterCriteriaSearchIds=%7C&FindCacheKey=FindLocationCacheKey_08081496-a4cb-400a-9530-b093e00ceec3&FindInRadius=&FindLatitude=40.7508&FindLongitude=-73.996122&SortDirectionField=distance&defaultMapView=False&SelectedCity=&SelectedCity=&SelectedState=&SelectedZip=10001&SelectedZip=10001&SelectedLocationName=&SelectedLocationName=&SelectedLocationDepartmentTypeId=&cityTxt1=&SelectedState=&zipTxt1=10001&SelectedConsumerLocation="

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="card card-media card-location"]')
    total = int(dom.xpath('//strong[@id="locationTotal_top"]/text()')[0])
    for page_index in range(2, total // 18 + 2):
        response = session.get(
            add_or_replace_parameter(page_url, "PageIndex", str(page_index))
        )
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="card card-media card-location"]')

    for poi_html in all_locations:
        url = poi_html.xpath('.//div[@class="card__body"]/a/@href')[0]
        loc_url = urljoin(start_url, url)
        address_raw = poi_html.xpath(".//address/text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw) == 3:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        location_name = poi_html.xpath(".//h5/text()")
        location_name = (
            location_name[0].split("-")[0].strip().split("–")[0].strip()
            if location_name
            else "<MISSING>"
        )
        street_address = address_raw[0]
        city = address_raw[1].split(",")[0]
        state = address_raw[1].split(",")[-1].split()[0]
        zip_code = address_raw[1].split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        if loc_url.split("/")[-1].isdigit():
            store_number = loc_url.split("/")[-1]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        store_response = session.get(loc_url)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath(
            '//ul[@class="list-unstyled text-muted zebra-hours"]/li/span/text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        location_type = store_dom.xpath(
            '//div[@class="row find-service-list"]//a/text()'
        )
        location_type = ", ".join(location_type) if location_type else "<MISSING>"

        item = [
            DOMAIN,
            loc_url,
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

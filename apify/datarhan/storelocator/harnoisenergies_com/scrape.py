import csv
import json
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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "https://harnoisenergies.com/en/brands/petro-t/"
    start_url = "https://harnoisenergies.com/fr/nos-stations-service/?fwp_station_banners=harnois"
    formdata = {
        "action": "facetwp_refresh",
        "data[facets]": '{"station_banners":["harnois"],"station_area":[],"station_main_services":[],"station_restauration":[],"station_promotions":[],"station_alternate_energy":[]}',
        "data[http_params][get][fwp_station_banners]": "harnois",
        "data[http_params][uri]": "en/service-stations",
        "data[http_params][url_vars][station_banners][]": "harnois",
        "data[http_params][lang]": "en",
        "data[template]": "wp",
        "data[extras][pager]": "true",
        "data[extras][sort]": "default",
        "data[extras][sortlat]": "46.017911",
        "data[extras][sortlng]": "-73.3965646",
        "data[soft_refresh]": "0",
        "data[is_bfcache]": "1",
        "data[first_load]": "0",
        "data[paged]": "1",
    }
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)
    pages_html = etree.HTML(data["pager"])
    total_pages = pages_html.xpath('//a[@class="facetwp-page last-page"]/@data-page')[0]
    page_dom = etree.HTML(data["template"])
    all_locations = page_dom.xpath('//div[@class="item"]')
    for page in range(2, int(total_pages) + 2):
        url = "https://harnoisenergies.com/fr/nos-stations-service/?fwp_station_banners=harnois&fwp_paged={}"
        formdata["data[paged]"] = str(page)
        response = session.post(url.format(str(page)), data=formdata, headers=headers)
        data = json.loads(response.text)
        page_dom = etree.HTML(data["template"])
        all_locations += page_dom.xpath('//div[@class="item"]')

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//h4/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@class="street"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@class="city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@class="province"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@class="postalcode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath(".//@data-hpgsiteid")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//span[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        types = poi_html.xpath('.//li[@class="stationOptions"]//img/@src')
        types = [
            elem.split("/")[-1]
            .split(".")[0]
            .replace("_Icon", "")
            .replace("_", " ")
            .replace("-", " ")
            for elem in types
        ]
        location_type = ", ".join(types) if types else "<MISSING>"
        geo = (
            poi_html.xpath('.//li[@class="itinerary"]/a/@href')[0]
            .split("/")[-1]
            .split(",")
        )
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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

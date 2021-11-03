import re
import csv
from lxml import etree
from urllib.parse import urljoin
from tqdm import tqdm
from tenacity import retry, stop_after_attempt
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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


session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)


@retry(stop=stop_after_attempt(3))
def get(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    return session.get(url, headers=headers)


@retry(stop=stop_after_attempt(3))
def post(url, data):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-microsoftajax": "Delta=true",
        "x-requested-with": "XMLHttpRequest",
    }
    return session.post(url, data, headers=headers)


def fetch_data():
    # Your scraper here

    items = []

    DOMAIN = "marcs.com"
    start_url = "https://www.marcs.com/Store-Finder"

    response = get(start_url)
    dom = etree.HTML(response.text)
    viewstate = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
    viewgen = dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for code in tqdm(all_codes):
        formdata = {
            "manScript": "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$UpdatePanel1|p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$submit",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "lng": "en-US",
            "p$lt$ctl01$SmartSearchBox$txtWord": "",
            "p$lt$ctl02$SmartSearchBox1$txtWord_exWatermark_ClientState": "",
            "p$lt$ctl02$SmartSearchBox1$txtWord": "",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$address": str(code),
            "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$radius": "50",
            "__VIEWSTATEGENERATOR": viewgen,
            "__SCROLLPOSITIONX": "0",
            "__SCROLLPOSITIONY": "0",
            "__ASYNCPOST": "true",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl03$Locations$submit": "Submit",
        }

        response = post(start_url, formdata)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(@id, "storelink")]/@href')
        response = get(start_url)
        dom = etree.HTML(response.text)
        viewstate = dom.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
        viewgen = dom.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]

    for url in tqdm(list(set(all_locations))):
        store_url = urljoin(start_url, url)
        loc_response = get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="display-text"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[@class="col-half sm-col-full"]/p/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0]
        city = address_raw[1].split(", ")[0]
        state = address_raw[1].split(", ")[-1].split()[0]
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = address_raw[-1].split(": ")[-1]
        location_type = "<MISSING>"
        latitude = re.findall("lat = \\'(.+?)\\'", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("lng = \\'(.+?)\\'", loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[h3[contains(text(), "Store Hours")]]/text()'
        )
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

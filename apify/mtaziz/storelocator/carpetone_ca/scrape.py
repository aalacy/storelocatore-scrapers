from sgrequests import SgRequests
from sglogging import SgLogSetup
import csv
import json
from lxml import html
import re
import time
from random import randint

logger = SgLogSetup().get_logger("carpetone_ca")
locator_domain_url = "https://www.carpetone.ca"
MISSING = "<MISSING>"

headers = {
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[1].strip(),
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
                row[11],
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)


# Get all worldwide tore URLs from Google Tag manager URL
url_google_tag_manager = "https://www.googletagmanager.com/gtm.js?id=GTM-M6N43L"
r_gtm = session.get(url_google_tag_manager, headers=headers)
pattern = r'{var a=\\\"(.*)\\".split'
url_all_stores_raw = re.findall(pattern, r_gtm.text)
url_all_stores_str = "".join(url_all_stores_raw)
url_all_stores_list = url_all_stores_str.split(" ")
url_all_stores_951 = list(set(url_all_stores_list))  # Deduped
url_all_stores_951.extend(
    ["http://www.irvinecarpetone.com"]
)  # irvinecarpetone was missing from Google Tag Manager
url_all_stores = url_all_stores_951
logger.info(f"Worldwide Number of Store URLs: {len(url_all_stores[0:10])}")
for url_cone in url_all_stores[0:10]:
    logger.info(
        f"Checking if we are getting Store URLs from Google Tag Manager URL: {url_cone} "
    )


def get_data_from_multi_locations(data_list, url_store_domain_check):
    items_multiloc = []
    data_list = data_list["Results"]
    logger.info(f"\nMulti locations data JSON: {data_list} \n")
    for data in data_list:
        locator_domain = locator_domain_url
        page_url_data = data["StoreAboutUrl"]
        if url_store_domain_check not in page_url_data:
            page_url_data = f"http://www.{url_store_domain_check}/{page_url_data}"
        else:
            page_url_data = page_url_data

        page_url = page_url_data or MISSING
        location_name = data["StoreName"] or MISSING

        # Street Address
        street_address = ""
        street_address_1 = data["StoreLocationSingle"]["Address"]
        street_address_2 = data["StoreLocationSingle"]["Address2"]
        if street_address_1:
            if street_address_2:
                street_address = f"{street_address_1} {street_address_2}"
            else:
                street_address = street_address_1
        else:
            street_address = MISSING

        c = data["StoreLocationSingle"]["City"]
        city = c if c else MISSING
        state = data["StoreLocationSingle"]["State"]
        state = state if state else MISSING
        division_code = data["StoreLocationSingle"]["DivisionCode"]
        if division_code:
            if division_code == "C-1CAN":
                country_code = "CA"
            elif division_code == "CPTONE":
                country_code = "US"
            else:
                country_code = division_code
        else:
            country_code = MISSING

        logger.info(f"Country Code: {country_code}")

        zip = data["StoreLocationSingle"]["Zip"] or MISSING
        store_number = data["StoreId"] if data["StoreId"] else MISSING
        phone = data["StorePhone"] if data["StorePhone"] else MISSING
        latitude = data["StoreLatitude"] or MISSING
        longitude = data["StoreLongitude"] or MISSING
        loctype = data["StoreLocationSingle"]["LocationType"]
        location_type = loctype if loctype else MISSING

        # Get hours of operation data
        hoo = []
        hoo_raw = data["StoreOpenHours"]
        for sort_order, h in enumerate(hoo_raw):
            h_hours = h["hours"].replace("-", "").strip()
            if h_hours:
                day_hours = f'{h["day"]} {h["hours"]}'
                hoo.append(day_hours)
            else:
                hours_of_operation = MISSING
        if hoo:
            hours_of_operation = "; ".join(hoo)
        else:
            hours_of_operation = MISSING
        if country_code == "CA":
            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            items_multiloc.append(row)
    return items_multiloc


def get_hours_raw_html(data_hours):
    xpath_col_store_hours = '//div[@class="col store-hours"]/dl/dd/ul'
    store_hours = data_hours.xpath(xpath_col_store_hours)
    store_hours_clean = []
    for sh in store_hours:
        week_day = sh.xpath("./li/span/text()")
        logger.info(f" Week Day: {week_day}")
        day_hours = sh.xpath("./li/text()")
        logger.info(f" Daily Hours: {day_hours}")

        for wd_idx, wd in enumerate(week_day):
            week_day_hours = f"{wd} {day_hours[wd_idx].strip()}"
            store_hours_clean.append(week_day_hours)
    if store_hours_clean:
        return "; ".join(store_hours_clean)
    else:
        MISSING


def get_data_from_website(data_raw):
    items_from_web = []
    try:
        data_type_json = data_raw.xpath('//script[@type="application/ld+json"]/text()')
        data_type_json = [x.replace("\r\n", "") for x in data_type_json]
        data_type_json = "".join(data_type_json).strip()
        data = json.loads(data_type_json)
        locator_domain = locator_domain_url
        page_url = data["url"] or MISSING
        location_name_xpath = '//li[@class="storeName"]/text()'
        location_name = "".join(data_raw.xpath(location_name_xpath))
        location_name = location_name if location_name else MISSING
        data_address = data["address"]
        street_address = (
            data_address["streetAddress"] if data_address["streetAddress"] else MISSING
        )
        city = data_address["addressLocality"] or MISSING
        state = data_address["addressRegion"] or MISSING
        country_code = data_address["addressCountry"]

        # C-1CAN refers to the division code that in turn happens to be Carpetone Canada
        # It is also used to indentify country code
        # CPTONE refers to the store those are located in the United States
        if country_code:
            if country_code == "Canada":
                country_code = "CA"
            elif country_code == "United States":
                country_code = "US"
            else:
                country_code = country_code
        else:
            country_code = MISSING
        logger.info(f"Country Code: {country_code} ")
        zip = data_address["postalCode"] or MISSING
        xpath_store_num = "//script/@data-cca-location-number"
        store_num = data_raw.xpath(xpath_store_num)
        store_number = "".join(store_num)
        phone = data["telephone"].strip()
        xpath_phone = '//a[@class="btn style1 var1 call-store desktop-only"]/@href'
        phone_data = data_raw.xpath(xpath_phone)
        phone_data = "".join(phone_data).replace("tel:", "").strip()

        if phone:
            phone = phone
        elif phone_data:
            phone = phone_data
        else:
            phone = MISSING

        location_type = data["@type"] or MISSING
        latlong_xpath = '//input[@id="location-latlong"]/@value'
        latlong_data = data_raw.xpath(latlong_xpath)
        latlong_data = "".join(latlong_data)
        try:
            latitude = latlong_data.split(",")[0]
            longitude = latlong_data.split(",")[-1]
        except Exception:
            latitude = MISSING
            longitude = MISSING
        hoo = data["openingHours"].strip()
        if hoo:
            hoo = hoo.replace("-", " - ")
            hours_of_operation = hoo
        else:
            hours_of_operation = get_hours_raw_html(data_raw)
        if country_code == "CA":
            row = [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
            items_from_web.append(row)
    except Exception:
        pass
    return items_from_web


def fetch_data():
    items = []
    for idx1, url_store_domain in enumerate(url_all_stores):
        try:
            url_store = f"http://www.{url_store_domain}"
            logger.info(f"Pulling the data from: {idx1}: {url_store} ")
            r = session.get(url_store)
            time.sleep(randint(3, 5))
            data_raw = html.fromstring(r.text, "lxml")
            logger.info(f"checking if it has muluti locations : {url_store}")
            xpath_if_multilocation_comment_available = (
                '//div[@class="multi-location"]/div/div/ul/li/text()'
            )
            url_multiloc_api = data_raw.xpath(xpath_if_multilocation_comment_available)
            url_multiloc_api = "".join(url_multiloc_api)

            if url_multiloc_api:
                url_multiloc_api_full = f"{locator_domain_url}{url_multiloc_api}"
                logger.info(
                    f"It has found multi locations and data : {url_multiloc_api_full} "
                )
                data_from_api_call = session.get(
                    url_multiloc_api_full, headers=headers
                ).json()
                items_from_api_list = get_data_from_multi_locations(
                    data_from_api_call, url_store_domain
                )
                for ifal in items_from_api_list:
                    items.append(ifal)
            else:
                # This will check if other locations exist for this store
                xpath_our_other_locations = '//div[h3[contains(text(), "Our Other Locations")]]/div/div/ul/li/a[@class="store-details"]/@href'
                logger.info("Checking if there are other locations for this store")
                url_our_other_locations = data_raw.xpath(xpath_our_other_locations)
                logger.info(f"Other Locations: {url_our_other_locations} ")
                if url_our_other_locations:
                    logger.info(
                        f"Other locations found at : {url_our_other_locations} "
                    )
                    for uool in url_our_other_locations:
                        url_other_location = uool
                        r_other_location = session.get(
                            url_other_location, headers=headers
                        )
                        data_r_other_location = html.fromstring(
                            r_other_location.text, "lxml"
                        )
                        items_from_our_other_locations = get_data_from_website(
                            data_r_other_location
                        )
                        for ifool in items_from_our_other_locations:
                            items.append(ifool)
                else:
                    items_from_website_list = get_data_from_website(data_raw)
                    for ifwl in items_from_website_list:
                        items.append(ifwl)
        except Exception:
            pass
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

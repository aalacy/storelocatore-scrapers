from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgFirefox
from webdriver_manager.firefox import GeckoDriverManager
import json
import time
from lxml import html
import re
import phonenumbers
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


DOMAIN = "https://www.essendant.com"
URL_LOCATION = "https://www.essendant.com/about-us/locations/"
URL_LOCATION_GOOGLE = (
    "https://www.google.com/maps/d/viewer?mid=1bOZ6ioaWIZmW9-0X2rp_MuSsF8Ur4Ksb"
)
MISSING = "<MISSING>"

logger = SgLogSetup().get_logger("essendant_com")

headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


session = SgRequests()
google_url_all_left_pane_store_list = (
    "https://www.google.com/maps/d/viewer?mid=1bOZ6ioaWIZmW9-0X2rp_MuSsF8Ur4Ksb"
)
rg = session.get(google_url_all_left_pane_store_list, headers=headers)
sel_rg = html.fromstring(rg.text, "lxml")
var_page_data = "".join(
    sel_rg.xpath('//script[contains(text(), "var _pageData")]/text()')
)
vpd = var_page_data.split("pageData = ")[-1].split(";")[0]
data_json = json.loads(vpd)
data_json = json.loads(data_json)
data_str = str(data_json[1:])
essendant_locs1 = data_str.split("Business Offices & Call Centers")[0]

# Business office and Call Centers
business_office_and_call_centers_locs = data_str.split(
    "Business Offices & Call Centers"
)[1]

essendant_locs2 = essendant_locs1.split(
    "https://mt.googleapis.com/vt/icon/name=icons/onion/SHARED-mymaps-pin-container"
)

# Essendant Locations
essendant_locs3 = essendant_locs2[:-2]


def get_store_urls_from_google_map():

    # Get Store URLs from Google Map
    all_store_urls = []
    with SgFirefox(
        executable_path=GeckoDriverManager().install(), is_headless=True
    ) as driver:
        driver.get(URL_LOCATION_GOOGLE)
        driver.implicitly_wait(30)
        load_more = driver.find_element_by_xpath('//span[contains(text(), "more")]')
        driver.execute_script("arguments[0].scrollIntoView();", load_more)
        driver.execute_script("arguments[0].click();", load_more)
        time.sleep(10)
        divs = driver.find_elements_by_xpath(
            '//div[div[label[contains(text(), "Essendant Locations")]]]/div[3]/div/div[2]/div'
        )
        for idx_div, div in enumerate(divs[0:]):
            driver.execute_script("arguments[0].click();", div)
            logger.info("Link Clicked with Success")
            time.sleep(20)
            view_in_google_map_url = [
                store_url.get_attribute("href")
                for store_url in driver.find_elements_by_xpath(
                    '//a[contains(text(), "View in Google Maps")]'
                )
            ]
            all_store_urls.extend(view_in_google_map_url)
            back = driver.find_element_by_xpath('//div[@aria-label="Back"]')
            driver.execute_script("arguments[0].click();", back)
            time.sleep(20)
            logger.info("Returned to the main page")
    logger.info(f"Scraping done with store urls | Total stores: {len(all_store_urls)}")
    return all_store_urls


def get_hoo(response_g):
    rtext = response_g.text
    hours_found = re.findall(
        r"(\bWednesday\b|\bThursday\b|\bFriday\b|\bSaturday\b|\bSunday\b|\bMonday\b|\bTuesday\b)|(\d+(AM|PM)–\d+(AM|PM))|(Closed)",
        rtext,
    )
    hoo = []
    hours_found_14 = hours_found[0:14]
    days = hours_found_14[0::2]
    days_new = []
    for i in days:
        days2 = ""
        for j in i:
            if j == "":
                continue
            else:
                days2 = j
        days_new.append(days2)
    hours = hours_found_14[1::2]
    hours_new = []
    for i in hours:
        i_list = list(i)
        hours2 = ""
        for j in i_list:
            if j == "AM" or j == "PM" or j == "":
                continue
            else:
                hours2 = j
        hours_new.append(hours2)

    for day_num, dn in enumerate(days_new):
        day_time = f"{dn} {hours_new[day_num]}"
        hoo.append(day_time)

    hoo = "; ".join(hoo)
    hours_of_operation = hoo
    hours_of_operation = hours_of_operation if hours_of_operation else MISSING
    logger.info(f"Hours of Operation: {hours_of_operation}")
    return hours_of_operation


def fetch_data():
    # This site does not directly contain the data for the stores
    # The URL is pulled from Google map
    store_urls = get_store_urls_from_google_map()
    session = SgRequests()
    for idx, item in enumerate(essendant_locs3[0:]):
        latlng_plus_location_name = str(item).split("'0', None")[-1]
        location_name_pattern = r"\[\[(.*?)\]\]"
        locname_found = re.findall(location_name_pattern, latlng_plus_location_name)
        locator_domain = DOMAIN
        location_name = "".join(locname_found).replace("'", "")
        logger.info(f"Location Name: {location_name}")
        page_url = MISSING
        latlng_pattern = r"\d+\.\d+,\s*[-]\d+\.\d+"
        latlng = re.findall(latlng_pattern, latlng_plus_location_name)
        latitude = latlng[0].split(",")[0].strip()
        longitude = latlng[0].split(",")[1].strip()
        logger.info(f"{idx} : ({latitude}, {longitude})")
        r_gmap = session.get(store_urls[idx], headers=headers)
        logger.info(f"Redirected Google URL: {r_gmap.url}")
        logger.info(f"Pulling the data from {idx}: {store_urls[idx]} ")
        d_gmap = html.fromstring(r_gmap.text, "lxml")
        meta_name = d_gmap.xpath('//meta[@itemprop="name"]/@content')
        meta_name = "".join(meta_name)
        meta_name = " ".join(meta_name.split())
        address = meta_name.split("·")[-1].strip()
        street_address = address.split(",")[0]
        city = address.split(",")[1]
        state = address.split(",")[2].strip().split(" ")[0]
        zip_postal = address.split(",")[2].strip().split(" ")[1]
        logger.info(
            f"Street Address: {street_address} | City: {city} | State: {state} | Zip : {zip_postal}"
        )
        country_code = "US"
        store_number = MISSING
        phone = r_gmap.text.split("tel:")[-1].split("\\")[0]
        phone = phonenumbers.format_number(
            phonenumbers.parse(phone, "US"), phonenumbers.PhoneNumberFormat.NATIONAL
        )
        phone = phone if phone else MISSING

        logger.info(f"Phone: {phone}")
        location_type = MISSING
        hours_of_operation = get_hoo(r_gmap)
        raw_address = address

        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    office_and_call_centers = business_office_and_call_centers_locs.split(
        "Business Name"
    )
    office_and_call_centers = office_and_call_centers[1:]
    for boaccl in office_and_call_centers:
        data_customer_care = (
            boaccl.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace("None", "")
            .replace("1,", "")
            .replace(",", "")
        )
        data_customer_care = " ".join(data_customer_care.split())
        address = data_customer_care.split("Address")
        locator_domain = DOMAIN
        page_url = MISSING
        location_name = address[0].strip()
        logger.info(f"Location Name: {location_name}")
        address1 = address[1].split("City")
        logger.info(f"Address1: {address1}")
        street_address = address1[0].strip()
        logger.info(f"Street Address: {street_address}")

        address2 = address1[1].split("State ")
        city = address2[0].strip()
        logger.info(f"City: {city}")

        address3 = address2[1].split("Country")
        state = address3[0].strip()
        logger.info(f"State: {state}")

        address4 = address3[1].split("Postal code")
        country_code = "US"

        logger.info(f"Country: {country_code}")

        address5 = address4[1].split("Phone")
        zip_postal = address5[0].strip()
        logger.info(f"Zip: {zip_postal}")
        address6 = address5[1].strip().split(" ")

        phone = " ".join(address6[0:2]).strip()
        store_number = address6[2].strip()
        location_type = "Business Offices & Call Centers"
        latitude = address6[4].strip()
        longitude = address6[5].strip()
        if "F57C00" == latitude:
            latitude = MISSING
        if "1200" == longitude:
            longitude = MISSING
        hours_of_operation = MISSING
        raw_address = MISSING
        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Scraping Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import SgLogSetup
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium import SgChrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgpostal.sgpostal import parse_address_intl
import time
import ssl
from lxml import html
import json


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

MISSING = SgRecord.MISSING
DOMAIN = "laurier-optical.com"
logger = SgLogSetup().get_logger(logger_name="laurieroptical_com")
LOCATION_URL = "https://www.laurier-optical.com/locations"
headers = {
    "accept": "application/json, text/plain, */*",
    "Referer": "https://www.laurier-optical.com/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
}


def get_json_data_from_features_master_page(http, url):
    response1 = http.get(url, headers=headers)
    body = html.fromstring(response1.text, "lxml")
    url_features_master_page = body.xpath(
        '//link[contains(@id, "features_") and @id != "features_masterPage"]/@href'
    )[0]
    response2 = http.get(url_features_master_page, headers=headers)
    return {"data": json.loads(response2.text), "body": body}


def get_province_based_urls():
    with SgRequests() as http:
        r1 = http.get(LOCATION_URL, headers=headers)
        tree1 = html.fromstring(r1.text, "lxml")
        urls_followed_by_province = tree1.xpath(
            '//a[@data-testid="linkElement" and contains(@href, "eye-exam")]/@href'
        )
        logger.info(f"All province based urls: \n{urls_followed_by_province}")
        return urls_followed_by_province


def get_driver(url, class_name, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


def get_lat_lng(url):
    lat = None
    lng = None
    class_name = "_3Xz9Z"
    driver = get_driver(url, class_name)
    iframe = driver.find_element_by_xpath('//iframe[@class="_3Xz9Z"]')
    driver.switch_to.frame(iframe)
    time.sleep(10)
    pgsrc = driver.page_source
    try:
        sel_selenium = html.fromstring(pgsrc, "lxml")
        map_url = sel_selenium.xpath("//iframe/@src")[0]
        map_url_latlng = map_url.split("!2d")[-1]
        map_url_lng = map_url_latlng.split("!3d")[0]
        map_url_lat = map_url_latlng.split("!3d")[-1]
        map_url_lat = map_url_lat.split("!2m")[0]
        lat = map_url_lat
        lng = map_url_lng
    except:
        lat = MISSING
        lng = MISSING

    return lat, lng


# Thurston
def get_latlng_for_thurston(http: SgRequests):
    # This returns the latlng for Laurier Optical Thurston
    urls_followed_by_province = get_province_based_urls()
    locations = None
    if "https://www.laurier-optical.com/eye-exam-ottawa" in urls_followed_by_province:
        urls_followed_by_province = ["https://www.laurier-optical.com/eye-exam-ottawa"]
        for idx, url_province in enumerate(urls_followed_by_province[0:1]):
            logger.info(f"Page URL TESTING: {urls_followed_by_province[idx]}")
            page_url = urls_followed_by_province[idx]
            logger.info(f"page_url: {page_url}")
            logger.info(f"[{idx}] Pulling the data from: {url_province} ")
            response_dict = get_json_data_from_features_master_page(http, url_province)
            data = response_dict["data"]
            location_name = ""
            for j in data["props"]["render"]["compProps"].values():
                skin = j.get("skin") or ""
                if "WRichTextNewSkin" in skin:
                    source = j.get("html") or "<html></html>"
                    if 'h2 class="font_2"' and 'span style="font-size:38px"' in source:
                        tree = html.fromstring(source)
                        location_name = tree.xpath(".//text()")[0]
                        logger.info(f"[{idx}] Location Name: {location_name}")

                    if "Monday" in source:
                        treeh = html.fromstring(source)
                        text = treeh.xpath(".//text()")
                        for t in text:
                            t1 = " ".join(t.split())
                            if not t1.strip() or "Teppan" in t1:
                                continue
                            if "+" in t1:
                                phone = t1
                                logger.info(f"Phone: {phone}")

                    if "Tuesday" in source:
                        treeh = html.fromstring(source)
                        text = treeh.xpath(".//text()")[1:]
                        logger.info(f"Text except first element: {text}")
                        hours_of_operation = text
                        hours_of_operation = [
                            " ".join(i.split()) for i in hours_of_operation
                        ]
                        hours_of_operation = [i for i in hours_of_operation if i]
                        hours_of_operation = [
                            i.replace("Tuesday:", "Tuesday: ")
                            .replace("Wednesday:", "Wednesday: ")
                            .replace("Thursday:", "Thursday: ")
                            .replace("Friday:", "Friday: ")
                            .replace("Saturday:", "Saturday: ")
                            for i in hours_of_operation
                        ]
                        hours_of_operation = "; ".join(hours_of_operation)
                        logger.info(f"[{idx}] HOO: {hours_of_operation}")

                if "GoogleMapSkin" in skin:
                    logger.info("GoogleMapSkin is found in skin")
                    locations = j["mapData"]["locations"][0]
                    logger.info(f"[{idx}] Locations data:{locations}")
                else:
                    continue

                add_raw = locations["address"]
                logger.info(f"[{idx}] Address: {add_raw} ")
                pai = parse_address_intl(add_raw)

                street_address = pai.street_address_1 or MISSING
                logger.info(f"[{idx}] Street Address: {street_address}")

                city = pai.city or MISSING
                logger.info(f"[{idx}] City: {city}")

                state = pai.state or MISSING
                logger.info(f"[{idx}] State: {state}")

                zip_postal = pai.postcode or MISSING
                logger.info(f"[{idx}] Zipcode: {zip_postal}")

                country_code = "CA"
                logger.info(f"[{idx}] Country Code: {country_code}")

                latitude = locations["latitude"]
                logger.info(f"[{idx}] Latitude: {latitude}")

                longitude = locations["longitude"]
                logger.info(f"[{idx}] Longitude: {longitude}")
                logger.info(f"Location Name: {location_name}")
                return latitude, longitude


def fetch_records_on(http: SgRequests):
    store_url_ontario = "https://www.laurier-optical.com/eye-exam-ontario"
    response_dict = get_json_data_from_features_master_page(http, store_url_ontario)
    data = response_dict["data"]
    comprops = data["props"]["render"]["compProps"]
    address_list = []
    location_name_list = []
    page_url_list = []
    phone_hoo_list = []

    for k, j in data["props"]["render"]["compProps"].items():
        hours_of_operation = None
        locator_domain = DOMAIN
        location_name = None
        street_address = None
        city = None
        state = None
        zip_postal = None
        pai = None
        phone = None
        page_url = None
        raw_address = None
        if "comp-kfpmqtmo__item" in k:
            k1 = k
            add_html = comprops[k1]["html"]
            sel_add = html.fromstring(add_html, "lxml")
            address_data = sel_add.xpath(
                '//span[contains(@style, "color:#000000")]/text()'
            )[0]
            pai = parse_address_intl(address_data)
            street_address = pai.street_address_1 or MISSING
            city = pai.city or MISSING
            state = pai.state or MISSING
            zip_postal = pai.postcode or MISSING
            logger.info(f"Zipcode: {zip_postal}")
            raw_address = address_data or MISSING
            address_row = (street_address, city, state, zip_postal, raw_address)
            address_list.append(address_row)

        if "comp-kfpmqtk4__item" in k:
            k2 = k
            locname_html = comprops[k2]["html"]
            sel_locname = html.fromstring(locname_html, "lxml")
            locname = sel_locname.xpath(
                '//span[contains(@style, "color:#000000")]/text()'
            )[0]
            location_name_list.append((locname))

        if "comp-kfpn314y__item" in k:
            k3 = k
            hoo_html = comprops[k3]["html"]
            sel_hoo = html.fromstring(hoo_html, "lxml")
            hoo = sel_hoo.xpath('//p[contains(@class, "font_8")]/text()')
            hours_of_operation = "; ".join(hoo)
            phone = sel_hoo.xpath('//a[contains(@href, "tel:")]/text()')[0]
            phone_hoo_list.append((phone, hours_of_operation))

        if "comp-kfpmqtmv__item" in k:
            k4 = k
            page_url = comprops[k4]["link"]["href"]
            logger.info(f"\nPage URL > link > href: {page_url} | {comprops[k4]}")
            page_url_list.append((page_url))

    for idx in range(0, len(address_list)):
        street_address, city, state, zip_postal, raw_address = address_list[idx]
        location_name = location_name_list[idx]
        phone, hours_of_operation = phone_hoo_list[idx]
        lat = ""
        lng = ""

        # Note: ( Laurier Optical Thurston ) does not have direct page_url like others.
        # we can get most of the page_url from https://www.laurier-optical.com/eye-exam-ontario -
        # but (Laurier Optical Thurston) eye exam center redirects to -
        # https://www.laurier-optical.com/eye-exam-ottawa - and it is found that
        # from Ottawa URL, we can get the latlng data for 9 stores, not for all which led
        # to use an alterantive method to get
        # latlng data from https://www.laurier-optical.com/eye-exam-ottawa

        page_url = page_url_list[idx]
        if "Laurier Optical Thurston" in location_name:
            lat, lng = get_latlng_for_thurston(http)
        else:
            lat, lng = get_lat_lng(page_url)
        logger.info(f"Street Address: {street_address}")
        logger.info(f"City: {city}")
        if "Ontario" in state:
            state = "ON"
        logger.info(f"State: {state}")
        country_code = "CA"
        logger.info(f"Country Code: {country_code}")

        latitude = lat
        logger.info(f"Latitude: {latitude}")

        longitude = lng
        logger.info(f"Longitude: {longitude}")

        item = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
        yield item


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            records = fetch_records_on(http)
            for rec in records:
                writer.write_row(rec)
                count = count + 1
    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

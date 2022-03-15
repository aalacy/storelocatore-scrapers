from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from webdriver_manager.firefox import GeckoDriverManager
from sgselenium import SgFirefox
import time
import json
from lxml import html
import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


MISSING = SgRecord.MISSING
DOMAIN = "mezzagrille.com"
LOCATION_URL = "https://mezzagrille.com/contact-us/"
logger = SgLogSetup().get_logger("mezzagrille_com")


headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
}


def get_google_map_urls():
    store_google_map_urls = []
    locnames_and_phones = []
    with SgFirefox(
        executable_path=GeckoDriverManager().install(), is_headless=True
    ) as driver:
        driver.maximize_window()
        driver.get(LOCATION_URL)
        time.sleep(20)
        map_bubble_zindex0_xpath = (
            '//div[@role="button" and contains(@style, "z-index: 0;")]/img'
        )
        map_bubble_zindex1_xpath = (
            '//div[@role="button" and contains(@style, "z-index: 1;")]/img'
        )
        map_bubble_zindex2_xpath = (
            '//div[@role="button" and contains(@style, "z-index: 2;")]/img'
        )
        map_bubble_zindex3_xpath = (
            '//div[@role="button" and contains(@style, "z-index: 3;")]/img'
        )
        map_bubble_zindex4_xpath = (
            '//div[@role="button" and contains(@style, "z-index: 4;")]/img'
        )

        close_gif_xpath = '//img[contains(@src, "https://www.google.com/intl/en_us/mapfiles/close.gif")]'

        # Z index 0 ( 1st Store)
        driver.find_element_by_xpath(map_bubble_zindex0_xpath).click()
        time.sleep(10)
        # Grab the 1st store Google Map URL
        sel0 = html.fromstring(driver.page_source, "lxml")
        gurl0 = sel0.xpath('//script[contains(@src, "GetPlaceDetails")]/@src')
        gurl0 = list(set(gurl0))
        logger.info(f"Googleapis Get Place Details URL: {gurl0}")
        store_google_map_urls.extend(gurl0)
        # Grab Location Name and Phone Number
        ln0 = sel0.xpath('//p[@class="place-title"]/text()')
        ph0 = sel0.xpath(
            '//div[@class="place-phone"]/a[contains(@href, "tel:")]/text()'
        )
        logger.info(f"LocName 0: {ln0} | Phone 0: {ph0}")
        locnames_and_phones.append((ln0, ph0))
        # Close the window
        driver.find_element_by_xpath(close_gif_xpath).click()

        # Z index 1 ( 2nd Store)
        driver.find_element_by_xpath(map_bubble_zindex1_xpath).click()
        time.sleep(10)
        # Grab the 2nd store Google Map URL
        sel1 = html.fromstring(driver.page_source, "lxml")
        gurl1 = sel1.xpath('//script[contains(@src, "GetPlaceDetails")]/@src')
        gurl1 = list(set(gurl1))
        logger.info(f"Googleapis Get Place Details URL: {gurl1}")

        store_google_map_urls.extend(gurl1)
        # Grab Location Name and Phone Number
        ln1 = sel1.xpath('//p[@class="place-title"]/text()')
        ph1 = sel1.xpath(
            '//div[@class="place-phone"]/a[contains(@href, "tel:")]/text()'
        )
        logger.info(f"LocName 1: {ln1} | Phone 1: {ph1}")
        locnames_and_phones.append((ln1, ph1))
        driver.find_element_by_xpath(close_gif_xpath).click()

        # Z index 2 ( 3rd Store )
        driver.find_element_by_xpath(map_bubble_zindex2_xpath).click()
        time.sleep(10)
        sel2 = html.fromstring(driver.page_source, "lxml")
        gurl2 = sel2.xpath('//script[contains(@src, "GetPlaceDetails")]/@src')
        gurl2 = list(set(gurl2))
        logger.info(f"Googleapis Get Place Details URL: {gurl2}")

        store_google_map_urls.extend(gurl2)
        # Grab Location Name and Phone Number
        ln2 = sel2.xpath('//p[@class="place-title"]/text()')
        ph2 = sel2.xpath(
            '//div[@class="place-phone"]/a[contains(@href, "tel:")]/text()'
        )
        logger.info(f"LocName 2: {ln2} | Phone 2: {ph2}")
        locnames_and_phones.append((ln2, ph2))
        # Close the Window
        driver.find_element_by_xpath(close_gif_xpath).click()

        # Z index 3 ( 4th Store )
        driver.find_element_by_xpath(map_bubble_zindex3_xpath).click()
        time.sleep(10)
        sel3 = html.fromstring(driver.page_source, "lxml")
        gurl3 = sel3.xpath('//script[contains(@src, "GetPlaceDetails")]/@src')
        gurl3 = list(set(gurl3))
        logger.info(f"Googleapis Get Place Details URL: {gurl3}")
        store_google_map_urls.extend(gurl3)
        # Grab Location Name and Phone Number
        ln3 = sel3.xpath('//p[@class="place-title"]/text()')
        ph3 = sel3.xpath(
            '//div[@class="place-phone"]/a[contains(@href, "tel:")]/text()'
        )
        logger.info(f"LocName 3: {ln3} | Phone 3: {ph3}")
        locnames_and_phones.append((ln3, ph3))
        # Close the Window
        driver.find_element_by_xpath(close_gif_xpath).click()

        # Z index 4 ( 5th Store )
        driver.find_element_by_xpath(map_bubble_zindex4_xpath).click()
        time.sleep(20)
        sel4 = html.fromstring(driver.page_source, "lxml")
        gurl4 = sel4.xpath('//script[contains(@src, "GetPlaceDetails")]/@src')
        gurl0 = list(set(gurl0))
        logger.info(f"Googleapis Get Place Details URL: {gurl0}")
        store_google_map_urls.extend(gurl4)
        # Grab Location Name and Phone Number
        ln4 = sel4.xpath('//p[@class="place-title"]/text()')
        ph4 = sel4.xpath(
            '//div[@class="place-phone"]/a[contains(@href, "tel:")]/text()'
        )
        logger.info(f"LocName 4: {ln4} | Phone 4: {ph4}")
        locnames_and_phones.append((ln4, ph4))
        # Close the Window
        driver.find_element_by_xpath(close_gif_xpath).click()
    logger.info("Grabbing Google Map URL Finished!!")
    return (locnames_and_phones, store_google_map_urls)


location_names, gmap_urls = get_google_map_urls()


def get_ordered_locnames_and_gurls():
    s = SgRequests()
    r = s.get(LOCATION_URL)
    sel_gmb_data = html.fromstring(r.text, "lxml")
    gmb_data = sel_gmb_data.xpath('//script[contains(text(), "var gmb_data")]/text()')
    gmb_data = "".join(gmb_data).split("gmb_data =")[-1]
    gmb_data = gmb_data.split(";")[0].lstrip().rstrip()
    gmb_data = json.loads(gmb_data)
    locname_and_place_id = []
    for i in gmb_data["1227"]["map_markers"]:
        gmb_data_dict = {"title": i["title"], "place_id": i["place_id"]}
        locname_and_place_id.append(gmb_data_dict)
    gmap_urls1 = list(set(gmap_urls))
    ordered_gmap_urls_and__locnames = []
    for i in locname_and_place_id:
        for j in gmap_urls1:
            if i["place_id"] in j:
                k = (j, i["title"])
                ordered_gmap_urls_and__locnames.append(k)
    locname_and_description = []
    for i in gmb_data["1227"]["map_markers"]:
        try:
            gmb_coming_soon = {"title": i["title"], "coming_soon": i["description"]}
        except KeyError:
            gmb_coming_soon = {"title": i["title"], "coming_soon": MISSING}

        locname_and_description.append(gmb_coming_soon)

    return (locname_and_description, ordered_gmap_urls_and__locnames)


loctype, ordered_gmap_urls_and_location_names = get_ordered_locnames_and_gurls()


def fetch_data():
    with SgRequests() as session:
        for idx, gurl in enumerate(ordered_gmap_urls_and_location_names[0:]):
            locator_domain = DOMAIN
            page_url = LOCATION_URL

            # We need to transform the data into JSON format
            r1 = session.get(gurl[0], headers=headers)
            data_raw1 = "{" + r1.text.split("( {")[-1]
            data_raw2 = data_raw1.lstrip().rstrip(")").split()
            data_raw2 = " ".join(data_raw2)
            data_json = json.loads(data_raw2)
            result_address = data_json["result"]["adr_address"]
            location_name = gurl[1]
            location_name = location_name if location_name else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            # Parse JSON data
            sel_result_address = html.fromstring(result_address, "lxml")

            street_address = sel_result_address.xpath(
                '//span[@class="street-address"]/text()'
            )
            street_address = "".join(street_address)
            street_address = street_address if street_address else MISSING
            logger.info(f"[{idx}] Street Address: {street_address}")

            city = sel_result_address.xpath('//span[@class="locality"]/text()')
            city = "".join(city)
            city = city if city else MISSING
            logger.info(f"[{idx}] City: {city}")

            state = sel_result_address.xpath('//span[@class="region"]/text()')
            state = "".join(state)
            state = state if state else MISSING
            logger.info(f"[{idx}] Location Name: {location_name}")

            zip_postal = sel_result_address.xpath('//span[@class="postal-code"]/text()')
            zip_postal = "".join(zip_postal)
            zip_postal = zip_postal if zip_postal else MISSING
            logger.info(f"[{idx}] Zip Postal: {zip_postal}")

            country_code = sel_result_address.xpath(
                '//span[@class="country-name"]/text()'
            )
            country_code = "".join(country_code)
            country_code = country_code if country_code else MISSING
            logger.info(f"[{idx}] country_code: {country_code}")

            store_number = MISSING
            phone = "".join(location_names[idx][1])
            phone = phone if phone else MISSING
            logger.info(f"[{idx}] Phone: {phone}")

            location_type = loctype[idx]["coming_soon"]
            if "coming soon" in location_type.lower():
                location_type = location_type
            else:
                location_type = MISSING

            latitude = data_json["result"]["geometry"]["location"]["lat"]
            latitude = latitude if latitude else MISSING
            logger.info(f"[{idx}] latitude: {latitude}")

            longitude = data_json["result"]["geometry"]["location"]["lng"]
            longitude = longitude if longitude else MISSING
            logger.info(f"[{idx}] longitude: {longitude}")

            hours_of_operation = MISSING

            raw_address = data_json["result"]["formatted_address"]
            raw_address = raw_address if raw_address else MISSING
            logger.info(f"[{idx}] raw_address: {raw_address}")

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
    logger.info("Started")
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

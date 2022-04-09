# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal import sgpostal as parser
from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager

from lxml import html
import time
import ssl


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


website = "nobakedcookiedough.com"
logger = SgLogSetup().get_logger("nobakedcookiedough_com")

headers = {
    "authority": "nobakedcookiedough.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


def parse_address(add):
    pai = parser.parse_address_usa(add)
    city = pai.city or ""
    state = pai.state or ""
    zc = pai.postcode or ""
    sta = ""
    sta1 = pai.street_address_1
    sta2 = pai.street_address_2
    if sta1 is not None and sta2 is None:
        sta = sta1
    elif sta1 is None and sta2 is not None:
        sta = sta2
    elif sta1 is not None and sta2 is not None:
        sta = sta1 + ", " + sta2
    else:
        sta = ""

    cc = pai.country or ""
    return city, state, zc, sta, cc


def get_latlng(state_and_zip, state_plus_pcode, drivers):
    lat = ""
    lng = ""

    # State and Zip example: "TN+37405"
    xpath1 = f"//iframe[contains(@src, '{state_and_zip}')]"
    frame1 = drivers.find_element_by_xpath(xpath1)
    drivers.switch_to.frame(frame1)
    pgsrc_frame1 = drivers.page_source
    latlng = pgsrc_frame1.split(state_plus_pcode)
    len_of_latlng = len(latlng)
    logger.info(f"length of latlng list: {len_of_latlng}")
    ll = latlng[1]
    logger.info("<<<=======================>>>>")
    logger.info(f"1st element: {latlng[0]}")
    logger.info(f"2nd element: {latlng[1]}")
    logger.info(f"3rd element: {latlng[2]}")
    ll_rep = ll.split("],")[0].replace("null,", "").replace('",[', "").split(",")
    lat = ll_rep[0]
    lng = ll_rep[1]
    logger.info(f"LatLng: ({lat}, {lng})")
    return lat, lng


def fetch_data(search_url, driver):
    with SgRequests(verify_ssl=False, timeout_config=400) as session:
        search_res = session.get(search_url, headers=headers)
        search_sel = html.fromstring(search_res.text)
        details_section = search_sel.xpath(
            '//div[contains(@class, "detail-sections")]/div[contains(@class, "block__map block__")]'
        )
        for ds in details_section:
            page_url = search_url
            location_name = "".join(
                ds.xpath('.//p[contains(@class, "location-name")]//text()')
            )
            logger.info(f"location name: {location_name}")

            add = "".join(
                ds.xpath(
                    './/*[contains(text(), "Address")]/following-sibling::p[1]/text()'
                )
            )
            logger.info(f"Address: {add}")

            hours = "".join(
                ds.xpath(
                    './/*[contains(text(), "Address")]/following-sibling::p[2]/text()'
                )
            )
            logger.info(f"HOO: {hours}")

            phone = "".join(
                ds.xpath(
                    './/*[contains(text(), "Address")]/following-sibling::p[3]/text()'
                )
            )
            logger.info(f"Phone: {phone}")

            map_link = "".join(
                ds.xpath(
                    './/a[contains(@aria-label,"Get directions to this location") and contains(., "Directions")]//@href'
                )
            )
            logger.info(f"map_link: {map_link}")

            # Parse the address using sgpostal
            city, state, zc, sta, cc = parse_address(add)
            logger.info(
                f"Address:\nCity: {city}\nState: {state}\nzipcode: {zc}\nStreet Address: {sta}\nCountry Code: {cc}"
            )

            # This ( state and postcode obtained from raw address )
            # will be used to identify particular iframe on the source
            state_plus_postcode = " " + state + " " + zc
            logger.info(f"state_plus_postcode: {state_plus_postcode}")

            state_plus_zip = state + "+" + zc
            if state == "MO":
                state_plus_zip = "Missouri" + "+" + zc

            # Every iframe holding the latlng data has different iframe
            # on the source, this is why to get the iframe loaded for each store
            # we need to get the response using selenium
            driver.get(search_url)
            time.sleep(10)
            logger.info(f"Pulling LatLng Data for {state_plus_zip} | {state_plus_zip}")
            lat, lng = get_latlng(state_plus_zip, state_plus_postcode, driver)
            raw_address = add
            logger.info(f"Raw Address: {raw_address}")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=sta,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=cc,
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=lat or "",
                longitude=lng or "",
                locator_domain=website,
                hours_of_operation=hours,
                raw_address=raw_address,
            )
            yield row


def scrape():

    # Note: Why selenium had to be used instead of sgselenium?
    # It is found that sgselenium with Proxy not working as
    # Google MAP API calls by sites internal calls being
    # denied to be loaded that lead to use selenium
    # instead of sgselenium.
    with SgChrome(
        executable_path=ChromeDriverManager().install(), is_headless=True
    ) as driver:
        search_url = "https://nobakedcookiedough.com/pages/visit-us"
        logger.info("Started")
        count = 0
        with SgWriter(
            deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
        ) as writer:
            results = fetch_data(search_url, driver)
            for rec in results:
                writer.write_row(rec)
                count = count + 1
        driver.quit()
        logger.info(f"No of records being processed: {count}")
        logger.info("Finished")


if __name__ == "__main__":
    scrape()

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from lxml import html
import time
import ssl
import random
from sgpostal.sgpostal import parse_address_intl


logger = SgLogSetup().get_logger(logger_name="tumi_com")
locator_domain_url = "tumi.com"
MAX_WORKERS = 4
MISSING = SgRecord.MISSING
INTL_TUMI_COM_URL = "https://intl.tumi.com"


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}


LOCATOR_URL_START = "https://intl.tumi.com/store-finder?q=Paris&searchRadius=8000.0&CSRFToken=783d1caa-f6c7-400d-ae0c-809429ab652b"

# location type identifier is considered to be just informational
location_type_identifier_images = {
    "store_pin_image_url": "https://cdn-fsly.yottaa.net/5c7577442bb0ac7a0f319914/intl.tumi.com/v~4b.404/_ui/desktop/common/images/tumiMarker.png?yocs=6_a_",
    "retailer_pin_image_url": "https://cdn-fsly.yottaa.net/5c7577442bb0ac7a0f319914/intl.tumi.com/v~4b.404/_ui/desktop/common/images/tumiRetailers.png?yocs=6_a_",
    "outlet_pin_image_url": "https://cdn-fsly.yottaa.net/5c7577442bb0ac7a0f319914/intl.tumi.com/v~4b.404/_ui/desktop/common/images/tumiOutlets.png?yocs=6_a_",
}
logger.info(f"Location Type Identifier Images:\n{location_type_identifier_images}")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests(verify_ssl=False) as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(10, 15))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def get_paginated_urls():
    rpagin = get_response(LOCATOR_URL_START)
    sel = html.fromstring(rpagin.text, "lxml")
    num_of_pages = sel.xpath('//*[contains(@class, "search-paging-info")]/text()')
    nofpages = num_of_pages[-1].strip()
    location_pages = []
    for pnum in range(0, int(nofpages)):
        location_url = f"https://intl.tumi.com/store-finder?q=Paris&searchRadius=8000.0&page={pnum}"
        location_pages.append(location_url)
    return location_pages


def get_hoo(sec_sel):
    xpath_hoo_lis = './/ul[@class="locator-hours"]/li'
    hoo_lis = sec_sel.xpath(xpath_hoo_lis)
    hoo = None
    hoo_list = []
    for hoo_li in hoo_lis:
        date = hoo_li.xpath('.//time[contains(@itemprop, "openingHours")]/@datetime')
        date = [" ".join(i.split()) for i in date]
        date = "".join(date)
        hoo_list.append(date)
    if hoo_list:
        hoo = ", ".join(hoo_list)
    else:
        hoo = MISSING
    hoo = hoo.strip().lstrip(",").strip()
    return hoo


def parse_add2(raw_add2):
    sta = ""
    city = ""
    state = ""
    zp = ""
    cc = ""
    zp_cc = raw_add2[-1].split("-")
    zp_cc = [i.strip() for i in zp_cc]
    if zp_cc[0]:
        zp = zp_cc[0]
    else:
        zp = MISSING
    if zp_cc[-1]:
        cc = zp_cc[-1]
    else:
        cc = MISSING
    sta1 = None
    sta2 = None
    try:
        sta1 = raw_add2[0]
        sta2 = raw_add2[1]
        sta = sta1 + ", " + sta2
        sta = " ".join(sta.split()).replace(" ,", ",")
    except:
        sta = MISSING
    try:
        cs = raw_add2[2]
        cs_s = cs.split(",")
        cs_s = [i.strip() for i in cs_s]
        city = cs_s[0]
        state = cs_s[1]
    except Exception as e:
        city = MISSING
        state = MISSING
        logger.info(f"Fix ParseAddressError: <<{e}>> for {raw_add2}")

    return sta, city, state, zp, cc


def get_latlng_storenum_purl(sel):
    google_maps_latlng = sel.xpath(
        '//script[contains(@type, "text/javascript") and contains(text(), "drawStoresFinal")]/text()'
    )
    gmll = google_maps_latlng[0].split(";")
    gmll_addstore = gmll[1:-1]
    gmll_addstore1 = [" ".join(i.split()) for i in gmll_addstore]
    gmll_addstore2 = [
        i.replace("addStore(new google.maps.LatLng(", "")
        .replace(")", "")
        .replace('"', "")
        for i in gmll_addstore1
    ]
    gmll_addstore3 = [
        (i.split(",")[0].strip(), i.split(",")[1].strip(), i.split(",")[2].strip())
        for i in gmll_addstore2
    ]
    # Latitude, longitude, store_number and page_url
    gmll_addstore4 = [
        (i[0], i[1], i[2], f"https://intl.tumi.com/store/{i[2]}?lat={i[0]}&long={i[1]}")
        for i in gmll_addstore3
    ]
    return gmll_addstore4


def get_parsed_address(tsta, tcity, tstate, tzp):
    parsed_sta = None
    parsed_city = None
    parsed_state = None
    parsed_zp = None
    pai = parse_address_intl(tsta)

    # Parsing street address
    psta1 = pai.street_address_1
    psta2 = pai.street_address_2
    if psta1 is not None and psta2 is not None:
        parsed_sta = psta1 + ", " + psta2
    elif psta1 is not None and psta2 is None:
        parsed_sta = psta1
    elif psta1 is None and psta2 is not None:
        parsed_sta = psta2
    else:
        parsed_sta = MISSING
    logger.info(f"Parsed street address: {parsed_sta}")

    # Parse City
    if MISSING in tcity:
        if pai.city is not None:
            parsed_city = pai.city
        else:
            parsed_city = MISSING
    else:
        parsed_city = tcity

    logger.info(f"Parsed City: {parsed_city}")

    # Parse state
    if MISSING in tstate:
        if pai.state is not None:
            parsed_state = pai.state
        else:
            parsed_state = MISSING
    else:
        parsed_state = tstate

    logger.info(f"Parsed state: {parsed_state}")

    # Parse zip
    if MISSING in tzp:
        if pai.postcode is not None:
            parsed_zp = pai.postcode
        else:
            parsed_zp = MISSING
    else:
        parsed_zp = tzp

    logger.info(f"Parsed state: {parsed_zp}")
    return parsed_sta, parsed_city, parsed_state, parsed_zp


def fetch_records(idx, url, sgw: SgWriter):
    r = get_response(url)
    sel = html.fromstring(r.text, "lxml")
    xpath_form_section = '//form[contains(@id, "myStoreForm")]/section[contains(@aria-label, "location")]'
    sections = sel.xpath(xpath_form_section)
    latlng_storenum_purl = get_latlng_storenum_purl(sel)
    for idx2, sec in enumerate(sections):
        locname = sec.xpath('.//h2[contains(@class, "locator-storename")]/text()')[0]
        locname = " ".join(locname.split())
        add = sec.xpath('.//div[contains(@class, "locator-address")]/text()')
        add1 = [" ".join(i.split()) for i in add]
        add2 = [i for i in add1 if i]
        sta, city, state, zp, cc = parse_add2(add2)
        logger.info(
            f"sta: {sta} | city: {city} | state: {state} | zip_postal: {zp} | country_code: {cc}"
        )

        raw_add = sta
        ret_sta, ret_city, ret_state, ret_zp = get_parsed_address(
            raw_add, city, state, zp
        )

        # Store Number and LatLng
        lat, lng, sn, purl = latlng_storenum_purl[idx2]
        page_url = purl

        city_from_purl = None
        state_from_purl = None
        if MISSING in ret_city or MISSING in ret_state:
            try:
                individual_r = get_response(page_url)
                insel = html.fromstring(individual_r.text, "lxml")
                city_purl = "".join(
                    insel.xpath(
                        '//span[contains(@itemprop, "addressLocality") and contains(@class, "addressTown")]/text()'
                    )
                )
                state_purl = "".join(
                    insel.xpath('//span[contains(@itemprop, "addressRegion")]/text()')
                )
                if city_purl:
                    city_from_purl = city_purl
                else:
                    city_from_purl = MISSING
                if state_purl:
                    state_from_purl = state_purl
                else:
                    state_from_purl = MISSING
            except Exception as e:
                logger.info(f"Please fix CityStateError from <{e}> for {page_url}")
        else:
            city_from_purl = ret_city
            state_from_purl = ret_state

        # Tel
        tel = "".join(sec.xpath('.//div[contains(@class, "locator-address")]/a/text()'))
        tel = tel if tel else MISSING

        # Hours of operation
        hoo_ret = get_hoo(sec)

        # Location Type
        # tumiMarker.png refers to Store
        # tumiRetailers.png refers to Retailer
        # tumiOutlets.png refers to Outlet

        store_png = "tumiMarker.png"
        outlet_png = "tumiOutlets.png"
        retailer_png = "tumiRetailers.png"
        xpath_tumi_pin = './/a[contains(@href, "/store/")]/img[@class="locator-marker left ctnr-locator-image"]/@data-yo-src'
        store_or_outlet_or_retailer = "".join(sec.xpath(xpath_tumi_pin))
        loctype = None
        try:
            if store_or_outlet_or_retailer:
                if store_png in store_or_outlet_or_retailer:
                    loctype = "Store"
                if outlet_png in store_or_outlet_or_retailer:
                    loctype = "Outlet"
                if retailer_png in store_or_outlet_or_retailer:
                    loctype = "Retailer"
            else:
                loctype = MISSING
        except Exception as e:
            logger.info(f"Fix LoctypeError: <<{e}>> for {store_or_outlet_or_retailer}")

        rec = SgRecord(
            locator_domain="tumi.com",
            page_url=page_url,
            location_name=locname,
            street_address=ret_sta,
            city=city_from_purl,
            state=state_from_purl,
            zip_postal=ret_zp,
            country_code=cc,
            store_number=sn,
            phone=tel,
            location_type=loctype,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hoo_ret,
            raw_address=raw_add,
        )
        if rec is not None:
            sgw.write_row(rec)


def fetch_data(sgw: SgWriter):
    all_urls = get_paginated_urls()
    logger.info(f"Number of Paginated URLs: {len(all_urls)}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        task = [
            executor.submit(fetch_records, idx, url, sgw)
            for idx, url in enumerate(all_urls[0:])
        ]
        for future in as_completed(task):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

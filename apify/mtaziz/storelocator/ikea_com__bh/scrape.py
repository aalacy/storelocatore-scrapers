from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
from sgpostal.sgpostal import parse_address_intl
import tenacity
from datetime import datetime
from lxml import html
import time
import ssl
import random


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


logger = SgLogSetup().get_logger(logger_name="ikea_com__bh")
locator_domain_url = "ikea.com/bh/en"
MAX_WORKERS = 6
MISSING = SgRecord.MISSING
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
}

# List of countries and it's corresponding store locator URLs
store_locator_list = [
    ("https://www.ikea.com/bh/en/stores", "Bahrain", "BH"),
    ("https://www.ikea.bg/stores/", "Bulgaria", "BG"),
    ("https://www.ikea.com/hr/hr/stores", "Croatia", "HR"),
    ("https://www.ikea.com.cy/katastimata/", "Cyprus", "CY"),
    ("https://www.ikea.com/in/en/stores/", "India", "IN"),
    ("https://www.ikea.com/ie/en/stores/", "Ireland", "IE"),
    ("https://www.ikea.com/jo/en/stores", "Jordan", "JO"),
    ("https://www.ikea.com/kw/en/stores/", "Kuwait", "KW"),
    ("https://www.ikea.com/mx/en/stores/", "Mexico", "MX"),
    ("https://www.ikea.com/ma/en/stores/", "Morocco", "MA"),
    ("https://www.ikea.pr/mayaguez/en/information/contact", "Puerto Rico", "PR"),
    ("https://www.ikea.com/qa/en/stores/doha/", "Qatar", "QA"),
    ("https://www.ikea.com/rs/sr/stores/", "Serbia", "RS"),
    ("https://www.ikea.com/sk/sk/stores/", "Slovakia", "SK"),
    ("https://www.ikea.com/si/sl/stores/", "Slovenia", "SI"),
    ("https://www.ikea.com/ua/uk/stores/", "Ukraine", "UA"),
]


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(3, 7))
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")

def get_domain(page_url):
    # Identify the domain for each country
    locator_domain = ""
    # 1 - Bahrain
    if "ikea.com/bh/en" in page_url:
        locator_domain = "ikea.com/bh/en"
    # 2 - Bulgeria
    if "ikea.bg" in page_url:
        locator_domain = "ikea.bg"
    # 3 - Croatia
    if "ikea.com/hr/hr" in page_url:
        locator_domain = "ikea.com/hr/hr"
    # 4 - Cyprus
    if "ikea.com.cy" in page_url:
        locator_domain = "ikea.com.cy"
    # 5 - India
    if "ikea.com/in/en" in page_url:
        locator_domain = "ikea.com/in/en"
    # 6 - Ireland
    if "ikea.com/ie/en" in page_url:
        locator_domain = "ikea.com/ie/en"
    # 7 - Jordan
    if "ikea.com/jo/en" in page_url:
        locator_domain = "ikea.com/jo/en"
    # 8 - Kuwait
    if "ikea.com/kw/en" in page_url:
        locator_domain = "ikea.com/kw/en"
    # 9 - Mexico
    if "ikea.com/mx/en" in page_url:
        locator_domain = "ikea.com/mx/en"
    # 10 - Morocco
    if "ikea.com/ma/en" in page_url:
        locator_domain = "ikea.com/ma/en"
    # 11 - Puerto Rico
    if "ikea.pr" in page_url:
        locator_domain = "ikea.pr"
    # 12 - Qatar
    if "ikea.com/qa/en" in page_url:
        locator_domain = "ikea.com/qa/en"
    # 13 - Serbia
    if "ikea.com/rs/sr" in page_url:
        locator_domain = "ikea.com/rs/sr"
    # 14 - Slovakia
    if "ikea.com/sk/sk" in page_url:
        locator_domain = "ikea.com/sk/sk"
    # 15 - Slovenia
    if "ikea.com/si/sl" in page_url:
        locator_domain = "ikea.com/si/sl"
    # 16 - Ukraine
    if "ikea.com/ua/uk" in page_url:
        locator_domain = "ikea.com/ua/uk"

    return locator_domain


def get_country_code(page_url):
    country_code = ""
    if "ikea.com/bh/en" in page_url:
        country_code = "BH"
    if "ikea.bg" in page_url:
        country_code = "BG"
    if "ikea.com/hr/hr" in page_url:
        country_code = "HR"
    if "ikea.com.cy" in page_url:
        country_code = "CY"
    if "ikea.com/in/en" in page_url:
        country_code = "IN"
    if "ikea.com/ie/en" in page_url:
        country_code = "IE"
    if "ikea.com/jo/en" in page_url:
        country_code = "JO"
    if "ikea.com/kw/en" in page_url:
        country_code = "KW"
    if "ikea.com/mx/en" in page_url:
        country_code = "MX"
    if "ikea.com/ma/en" in page_url:
        country_code = "MA"
    if "ikea.pr" in page_url:
        country_code = "PR"
    if "ikea.com/qa/en" in page_url:
        country_code = "QA"
    if "ikea.com/rs/sr" in page_url:
        country_code = "RS"
    if "ikea.com/sk/sk" in page_url:
        country_code = "SK"
    if "ikea.com/si/sl" in page_url:
        country_code = "SI"
    if "ikea.com/ua/uk" in page_url:
        country_code = "UA"
    return country_code


def get_latlng(map_link):
    if "z/data" in map_link:
        latlng = map_link.split("@")[1].split("z/data")[0]
        lat = latlng.split(",")[0].strip()
        lng = latlng.split(",")[1].strip()
    elif "ll=" in map_link:
        latlng = map_link.split("ll=")[1].split("&")[0]
        lat = latlng.split(",")[0]
        lng = latlng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        lat = map_link.split("!3d")[1].strip().split("!")[0].strip()
        lng = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        lat = map_link.split("/@")[1].split(",")[0].strip()
        lng = map_link.split("/@")[1].split(",")[1].strip()
    else:
        lat = "<MISSING>"
        lng = "<MISSING>"
    return lat, lng


def get_parsed_address(address1):
    street_address = None
    city = None
    state = None
    zip_postal = None
    pai = parse_address_intl(address1)
    street_address = (
        pai.street_address_1 if pai.street_address_1 is not None else MISSING
    )
    city = pai.city if pai.city is not None else MISSING
    state = pai.state if pai.state is not None else MISSING
    zip_postal = pai.postcode if pai.postcode is not None else MISSING
    return street_address, city, state, zip_postal


# 1 - Bahrain
def fetch_records_bh(sgw: SgWriter):
    store_locator_url = "https://www.ikea.com/bh/en/stores"
    r = get_response(store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    location_name = "".join(sel.xpath(xpath_locname))
    logger.info(f"Location Name: {location_name}")
    xpath_address = '//div[contains(@data-pub-type,"text")]/p/text()'
    address = sel.xpath(xpath_address)[1]
    address1 = address
    street_address, city, state, zip_postal = get_parsed_address(address1)
    phone = MISSING
    xpath_gmap_url = '//p[a[contains(text(), "Get directions")]]/a/@href'
    gurl = "".join(sel.xpath(xpath_gmap_url))
    lat, lng = get_latlng(gurl)
    xpath_hoo = '//p[*[contains(text(), "Store opening hours")]]/text()'
    hours_of_operation = ""
    hoo = sel.xpath(xpath_hoo)
    if hoo:
        hours_of_operation = ", ".join(hoo)
    else:
        hours_of_operation = MISSING
    logger.info(f"HOO: {hours_of_operation}")
    page_url = store_locator_url
    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


def get_store_urls_bg():
    url = "https://www.ikea.bg/stores/"
    logger.info(f"Pulling the data from {url}")
    r = get_response(url)
    sel = html.fromstring(r.text, "lxml")
    xpath_page_urls = '//div[@class="stores-content"]//div[contains(@class, "store-item")]/a[@class="absLink"]/@href'
    page_urls = sel.xpath(xpath_page_urls)
    page_urls = ["https://www.ikea.bg" + i for i in page_urls]
    logger.info(f"page_urls: {page_urls}")
    return page_urls


def get_hoo_clean(hours):
    hours_of_operation = None
    hoo = [" ".join(i.split()) for i in hours]
    hoo = [i for i in hoo if i]
    if hoo:
        hours_of_operation = "; ".join(hoo)
    else:
        hours_of_operation = MISSING
    logger.info(f"HOO: {hours_of_operation}")
    return hours_of_operation


# 2 - Bulgaria (BG)
def fetch_records_bg(sgw: SgWriter):
    page_urls = get_store_urls_bg()
    for page_url in page_urls:
        r = get_response(page_url)
        sel = html.fromstring(r.text, "lxml")
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")

        xpath_address = '//div[h5[contains(text(), "Информация за магазина")]]/p/text()'
        address = sel.xpath(xpath_address)
        address = [" ".join(i.split()) for i in address]
        address1 = address[0]
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        # Phone
        xpath_phone = '//*[contains(text(), "T:")]/text()'
        ph = sel.xpath(xpath_phone)
        ph = ph = [" ".join(i.split()) for i in ph]
        ph = "".join(ph).replace("T:", "")
        phone = ph.strip() if ph else MISSING

        xpath_gmap_url = '//p[a[contains(text(), "Get directions")]]/a/@href'
        gurl = "".join(sel.xpath(xpath_gmap_url))
        lat, lng = get_latlng(gurl)

        xpath_hoo = '//div[*[contains(text(), "На магазина")]]/p/text()'
        hoo = sel.xpath(xpath_hoo)
        hours_of_operation = get_hoo_clean(hoo)
        page_url = page_url
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 3 - Croatia ( HR )


def fetch_records_hr(sgw: SgWriter):
    hr_store_locator_url = "https://www.ikea.com/hr/hr/stores/"
    r = get_response(hr_store_locator_url)
    sel = html.fromstring(r.text, "lxml")

    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    location_name = "".join(sel.xpath(xpath_locname))
    logger.info(f"Location Name: {location_name}")

    xpath_address = '//div[*[contains(text(), "Adresa")]]/p/text()'
    address_raw = sel.xpath(xpath_address)
    logger.info(f"address in raw: {address_raw}")
    address_raw = [" ".join(i.split()) for i in address_raw]
    address1 = ", ".join(address_raw)
    logger.info(f"Address: {address1}")
    street_address, city, state, zip_postal = get_parsed_address(address1)

    # Phone
    xpath_phone = '//*[contains(text(), "T:")]/text()'
    ph = sel.xpath(xpath_phone)
    ph = ph = [" ".join(i.split()) for i in ph]
    ph = "".join(ph).replace("T:", "")
    phone = ph.strip() if ph else MISSING

    xpath_gmap_url = '//a[contains(@href, "IKEA+Alfreda+Nobela")]/@href'
    gurl = "".join(sel.xpath(xpath_gmap_url))
    logger.info(f"Google Map URL: {gurl}")
    lat, lng = get_latlng(gurl)

    xpath_hoo = '//div[*[contains(text(), "Radno vrijeme")]]/p/text()'
    hoo = sel.xpath(xpath_hoo)
    hours_of_operation = get_hoo_clean(hoo)
    page_url = hr_store_locator_url
    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=hr_store_locator_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


# 4 - Cyprus ( CY )


def cy_get_store_urls():
    cy_store_locator_url = "https://www.ikea.com.cy/katastimata/"
    logger.info(f"Pulling the data from {cy_store_locator_url}")
    r = get_response(cy_store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    xpath_page_urls = '//div[@class="stores-content"]//div[contains(@class, "store-item")]/a[@class="absLink"]/@href'
    page_urls = sel.xpath(xpath_page_urls)
    page_urls = ["https://www.ikea.com.cy" + i for i in page_urls]
    logger.info(f"page_urls: {page_urls}")
    return page_urls


def fetch_records_cy(sgw: SgWriter):
    page_urls = cy_get_store_urls()
    for page_url in page_urls:
        r = get_response(page_url)
        sel = html.fromstring(r.text, "lxml")
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")

        # Address
        xpath_address = (
            '//div[h5[contains(text(), "Πληροφορίες Καταστήματος")]]/p/text()'
        )
        address = sel.xpath(xpath_address)
        address = [" ".join(i.split()) for i in address]
        address1 = address[0]
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        # Phone
        xpath_phone = '//*[contains(text(), "T:")]/following-sibling::span[1]/text() | //*[contains(text(), "T:")]/span[1]/text()'
        ph = sel.xpath(xpath_phone)
        logger.info(f"Phone raw: {ph}")
        ph = ph = [" ".join(i.split()) for i in ph]
        ph = "".join(ph).replace("T:", "")
        phone = ph.strip() if ph else MISSING
        logger.info(f"Phone: {phone}")

        # Google Map URL
        xpath_gmap_url = (
            '//div[*[contains(text(), "Πληροφορίες Καταστήματος")]]/a/@href'
        )
        gurl = "".join(sel.xpath(xpath_gmap_url))
        gr = get_response(gurl)
        gurl_redirected = gr.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))

        # HOO
        xpath_hoo = '//div[*[contains(text(), "Καταστήματος")]]/p/text()'
        hoo = sel.xpath(xpath_hoo)
        hours_of_operation = get_hoo_clean(hoo)
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 5 - India (IN)


def fetch_records_in(sgw: SgWriter):
    in_store_locator_url = "https://www.ikea.com/in/en/stores/"
    r1 = get_response(in_store_locator_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator = (
        '//div[@class="i1ycpxq9 pub__designSystemText t91kxqv w1fdzi2f"]/h2/a/@href'
    )
    page_urls = sel1.xpath(xpath_store_locator)
    logger.info(f"page urls: {page_urls}")
    for page_url in page_urls:
        r2 = get_response(page_url)
        sel2 = html.fromstring(r2.text, "lxml")
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel2.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")

        # Address
        xpath_address1 = '//div[@class="i1ycpxq9 pub__designSystemText t91kxqv w1fdzi2f"]/p[contains(text(), "IKEA Store")]/text()'
        xpath_address2 = '//div[@class="i1ycpxq9 pub__designSystemText t91kxqv w1fdzi2f"][h4]/p/text()'
        address = sel2.xpath(f"{xpath_address1} | {xpath_address2}")
        address = [" ".join(i.split()) for i in address]
        logger.info(f"address raw: {address}")
        address1 = ", ".join(address)
        address1 = address1.replace("IKEA Store - ", "")
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        # Phone
        xpath_phone1 = '//p[*[contains(text(), "Call us:")]]/text()'
        xpath_phone2 = '//*[contains(text(), "Call us:")]/text()'
        ph = sel2.xpath(f"{xpath_phone1} | {xpath_phone2}")
        logger.info(f"Phone raw: {ph}")
        ph = ph = [" ".join(i.split()) for i in ph]
        ph = "".join(ph).replace("T:", "").replace("Call us:", "").strip()
        phone = ph.strip() if ph else MISSING
        logger.info(f"Phone: {phone}")

        # LatLng
        xpath_gmap_url_in = '//a[*[*[contains(text(), "Get directions")]]]/@href'
        gurl = "".join(sel2.xpath(xpath_gmap_url_in))
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))

        # HOO
        xpath_hoo = '//p[strong[contains(text(), "Store")]]/text()'
        hoo = sel2.xpath(xpath_hoo)
        hours_of_operation = get_hoo_clean(hoo)
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 6 - Ireland (IE)


def fetch_records_ie(sgw: SgWriter):
    ie_store_locator_url = "https://www.ikea.com/ie/en/stores/"
    r1 = get_response(ie_store_locator_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator = '//div[*[*[contains(text(), "Stores")]]]//a/@href'
    page_urls = sel1.xpath(xpath_store_locator)
    logger.info(f"page urls: {page_urls}")
    for page_url in page_urls:
        logger.info(f"Pulling the data from {page_url}")
        r2 = get_response(page_url)
        sel2 = html.fromstring(r2.text, "lxml")

        # Location Name
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel2.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")
        page_url = page_url

        # Address
        xpath_address = '//div[*[strong[starts-with(text(), "Address")]]]/p[contains(text(), "Dublin ")]/text()'
        address = sel2.xpath(xpath_address)
        address = [" ".join(i.split()) for i in address]
        logger.info(f"address raw: {address}")
        address1 = ", ".join(address)
        address1 = address1.replace("IKEA Store - ", "")
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        # Phone
        xpath_phone1 = '//p[*[contains(text(), "Call us:")]]/text()'
        xpath_phone2 = '//*[contains(text(), "Call us:")]/text()'
        ph = sel2.xpath(f"{xpath_phone1} | {xpath_phone2}")
        logger.info(f"Phone raw: {ph}")
        ph = ph = [" ".join(i.split()) for i in ph]
        ph = "".join(ph).replace("T:", "").replace("Call us:", "").strip()
        phone = ph.strip() if ph else MISSING
        logger.info(f"Phone: {phone}")

        # LatLng from Google Map URL
        xpath_gmap_url = '//a[*[*[contains(text(), "Get directions")]]]/@href'
        gurl = "".join(sel2.xpath(xpath_gmap_url))
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))

        # HOO
        xpath_hoo = '//p[strong[contains(text(), "Store")]]//text()'
        hoo = sel2.xpath(xpath_hoo)
        logger.info(f"HOO raw: {hoo}")
        hoo = [" ".join(i.split()) for i in hoo]
        hoo = [i for i in hoo if i]
        hours_of_operation = (" ".join(hoo)).replace("Store", "").strip()
        logger.info(f"HOO: {hours_of_operation}")
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 7 - Jordan (JO)


def fetch_records_jo(sgw: SgWriter):
    jo_store_locator_url = "https://www.ikea.com/jo/en/stores/"
    r1 = get_response(jo_store_locator_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator = '//div[contains(@tabindex, "-1")]/a/@href'
    page_urls = sel1.xpath(xpath_store_locator)
    logger.info(f"page urls: {page_urls}")
    for page_url in page_urls:
        logger.info(f"Pulling the data from {page_url}")
        r2 = get_response(page_url)
        sel2 = html.fromstring(r2.text, "lxml")
        # Location Name
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel2.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")
        page_url = page_url

        # Address
        xpath_address = '//div[contains(@class, "i1ycpxq9 pub__designSystemText t91kxqv w1fdzi2f")]/h4/text()'
        address = sel2.xpath(xpath_address)
        address = [" ".join(i.split()) for i in address]
        logger.info(f"address raw: {address}")
        address1 = ", ".join(address)
        address1 = address1.replace("IKEA Store - ", "")
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        # Phone
        xpath_phone1 = '//p[*[contains(text(), "Call us:")]]/text()'
        xpath_phone2 = '//*[contains(text(), "Call us:")]/text()'
        ph = sel2.xpath(f"{xpath_phone1} | {xpath_phone2}")
        logger.info(f"Phone raw: {ph}")
        ph = ph = [" ".join(i.split()) for i in ph]
        ph = "".join(ph).replace("T:", "").replace("Call us:", "").strip()
        phone = ph.strip() if ph else MISSING
        logger.info(f"Phone: {phone}")

        xpath_gmap_url = '//a[*[*[contains(text(), "Get directions")]]]/@href'
        gurl = "".join(sel2.xpath(xpath_gmap_url))
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))

        # HOO
        xpath_hoo = '//div[contains(@class, "i1ycpxq9 pub__designSystemText t91kxqv w1fdzi2f")]/h4/strong/text() | //div[contains(@class, "i1ycpxq9 pub__designSystemText t91kxqv w1fdzi2f")]/p[contains(text(), "Store opening")]/text()'
        hoo = sel2.xpath(xpath_hoo)
        logger.info(f"HOO raw: {hoo}")
        hoo = [" ".join(i.split()) for i in hoo]
        hoo = [i for i in hoo if i]
        hours_of_operation = (
            (" ".join(hoo)).replace("Store", "").replace("opening ", "").strip()
        )
        logger.info(f"HOO: {hours_of_operation}")
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 8 - Kuwait (KW)


def fetch_records_kw(sgw: SgWriter):
    kw_store_locator_url = "https://www.ikea.com/kw/en/stores/"
    logger.info(f"Pulling the data from {kw_store_locator_url}")
    r2 = get_response(kw_store_locator_url)
    sel2 = html.fromstring(r2.text, "lxml")
    address_hoo = '//div[h4[contains(text(), "Address")]]'
    ahoo = sel2.xpath(address_hoo)
    for idx, ah in enumerate(ahoo):
        xpath_locname = '//div[h2[contains(text(), "IKEA")]]/h2/text()'
        location_name = sel2.xpath(xpath_locname)
        location_name = location_name[idx]
        logger.info(f"Location Name: {location_name}")
        page_url = kw_store_locator_url

        add = ah.xpath(".//text()")
        add1 = [" ".join(i.split()) for i in add]
        add2 = [i for i in add1 if i]
        address1 = ", ".join(add2[1:3])
        logger.info(f"address raw: {address1}")
        address1 = address1.replace("IKEA Store - ", "")
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        xpath_phone1 = '//p[*[contains(text(), "Call us:")]]/text()'
        xpath_phone2 = '//*[contains(text(), "Call us:")]/text()'
        ph = sel2.xpath(f"{xpath_phone1} | {xpath_phone2}")
        logger.info(f"Phone raw: {ph}")
        ph = ph = [" ".join(i.split()) for i in ph]
        ph = "".join(ph).replace("T:", "").replace("Call us:", "").strip()
        phone = ph.strip() if ph else MISSING
        logger.info(f"Phone: {phone}")

        xpath_gmap_url = '//a[*[*[contains(text(), "Get directions")]]]/@href'
        gurl = "".join(sel2.xpath(xpath_gmap_url))
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))

        # HOO
        hoo = add2[4]
        logger.info(f"HOO raw: {hoo}")
        hours_of_operation = hoo
        logger.info(f"HOO: {hours_of_operation}")
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


def get_phone(sel2):
    phone = None
    xpath_phone1 = '//p[*[contains(text(), "Call us:")]]/text()'
    xpath_phone2 = '//*[contains(text(), "Call us:")]/text()'
    ph = sel2.xpath(f"{xpath_phone1} | {xpath_phone2}")
    logger.info(f"Phone raw: {ph}")
    ph = ph = [" ".join(i.split()) for i in ph]
    ph = "".join(ph).replace("T:", "").replace("Call us:", "").strip()
    phone = ph.strip() if ph else MISSING
    logger.info(f"Phone: {phone}")
    return phone


# 9 - Mexico (MX)
def fetch_records_mx(sgw: SgWriter):
    mx_store_locator_url = "https://www.ikea.com/mx/en/stores/"
    r1 = get_response(mx_store_locator_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator = '//a[contains(@class, "pub__btn")]/@href'
    page_urls = sel1.xpath(xpath_store_locator)
    logger.info(f"page urls: {page_urls}")
    for page_url in page_urls:
        logger.info(f"Pulling the data from {page_url}")
        r2 = get_response(page_url)
        sel2 = html.fromstring(r2.text, "lxml")
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel2.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")

        xpath_address_and_hoo = '//div[*[*[contains(text(), "How to get")]]]/p/text()'
        address_and_hoo = sel2.xpath(xpath_address_and_hoo)
        logger.info(f"address raw: {address_and_hoo}")
        address1 = address_and_hoo[0]
        address1 = address1.replace("IKEA Store - ", "")
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)
        phone = get_phone(sel2)

        xpath_gmap_url = '//a[contains(text(), "Click here to see the map")]/@href'
        gurl = "".join(sel2.xpath(xpath_gmap_url))
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
        hours_of_operation = ""
        try:
            hours_of_operation = address_and_hoo[1]
        except:
            hours_of_operation = MISSING
        logger.info(f"HOO: {hours_of_operation}")
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 10 - Morocco (MA)
def get_address_n_hoo_ma(retat1):
    address = ""
    hoo = ""
    try:
        add_hoo = [" ".join(i.split()) for i in retat1]
        add_hoo = [i for i in add_hoo if i][1:]
        add_hoo = ", ".join(add_hoo)
        raw_add = add_hoo.split("Store opening hours")[0]
        raw_hoo = add_hoo.split("Store opening hours")[1]
        logger.info(f"HOO Raw: {raw_hoo}")
        hoo = raw_hoo.strip().lstrip(":,").strip()
        hoo = hoo.replace("Free Wi-Fi is available in the store", "")
        hoo = hoo.replace("IKEA Morocco will be open the following hours:", "")
        hoo = hoo.strip().lstrip(",").strip().rstrip(".").strip().rstrip(",")

        logger.info(f"HOO: {hoo}")
        address = raw_add.strip().rstrip(",").strip()
        logger.info(f"Address: {address}")
    except:
        address = MISSING
        hoo = MISSING
    return address, hoo


def fetch_records_ma(sgw: SgWriter):
    ma_store_locator_url = "https://www.ikea.com/ma/en/stores/"
    r1 = get_response(ma_store_locator_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator = '//div[*[*[contains(text(), "Stores")]]]//a/@href'
    xpath_store_locator = '//div[contains(@tabindex, "-1")]/a/@href'
    page_urls = sel1.xpath(xpath_store_locator)
    logger.info(f"page urls: {page_urls}")
    for page_url in page_urls:
        logger.info(f"Pulling the data from {page_url}")
        r2 = get_response(page_url)
        sel2 = html.fromstring(r2.text, "lxml")
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel2.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")
        xpath_address_and_hoo = '//div[*[contains(text(), "Store opening")]]//text() | //div[*[*[contains(text(), "Store opening")]]]//text()'
        address = sel2.xpath(xpath_address_and_hoo)
        address1, hoo = get_address_n_hoo_ma(address)
        street_address, city, state, zip_postal = get_parsed_address(address1)
        phone = get_phone(sel2)

        xpath_gmap_url1 = '//a[*[*[contains(text(), "Get directions")]]]/@href'
        xpath_gmap_url2 = '//a[contains(@href, "https://www.google.com/maps")]/@href'
        xpath_gmap_url12 = f"{xpath_gmap_url1} | {xpath_gmap_url2}"
        gurl = "".join(sel2.xpath(xpath_gmap_url12))
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
        hours_of_operation = hoo
        logger.info(f"HOO: {hours_of_operation}")
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=phone,
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours_of_operation,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 11 - Puerto Rico (PR)


def get_add_ph_n_hoo_pr(sel):
    xpath_address_and_hoo = '//div[strong[contains(text(), "Address")]]//text()'
    at = sel.xpath(xpath_address_and_hoo)
    at1 = [" ".join(i.split()) for i in at]
    at2 = [i for i in at1 if i]
    at3 = " ".join(at2)
    at4 = [i for i in at3.split("Address:") if i][0]
    address = at4.split("Phone number")[0].strip()
    logger.info(f"Address in PR: {address}")

    add_at42 = at4.split("Phone number")[1]
    add_at43 = add_at42.split("Schedule:")

    phone = add_at43[0].strip().lstrip().rstrip()
    logger.info(f"Phone in PR: {phone}")
    hoo = add_at43[1].strip().lstrip().rstrip()
    logger.info(f"HOO in PR: {hoo}")
    return address, phone, hoo


def fetch_records_pr(sgw: SgWriter):
    pr_store_locator_url = "https://www.ikea.pr/mayaguez/en/information/contact"
    r = get_response(pr_store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    page_url = pr_store_locator_url
    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    xpath_locname = '//span[@class="picto-ikea-point"]/text()'
    xpath_locname = '//*[span[@class="picto-ikea-point"]]/text()'
    location_name = sel.xpath(xpath_locname)[0]
    logger.info(f"Location Name: {location_name}")
    address1, ph, hoo = get_add_ph_n_hoo_pr(sel)
    logger.info(f"Address: {address1}")
    street_address, city, state, zip_postal = get_parsed_address(address1)
    phone = ph.strip() if ph else MISSING
    xpath_gmap_url1 = '//a[*[*[contains(text(), "Get directions")]]]/@href'
    xpath_gmap_url2 = '//a[contains(@href, "https://www.google.com/maps")]/@href'
    xpath_gmap_url12 = f"{xpath_gmap_url1} | {xpath_gmap_url2}"
    xpath_gmap_url = '//div[contains(@class, "google-maps-link")]/a/@href'
    gurl = sel.xpath(xpath_gmap_url)
    lat = ""
    lng = ""
    if gurl:
        gurl = gurl[0]
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
    else:
        lat = MISSING
        lng = MISSING
    hours_of_operation = hoo
    logger.info(f"HOO: {hours_of_operation}")

    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


# 12 - Qatar (QA)


def remove_comma(d):
    c = d.strip().lstrip(",").rstrip(",").strip().lstrip(";").rstrip(";").lstrip(":")
    return c


def get_add_n_hoo_qa(raw_data):
    address = MISSING
    hoo = MISSING
    logger.info(f"Raw : {raw_data}")
    raw_data = raw_data[1:]
    raw_data = ", ".join(raw_data)
    logger.info(f"raw_data: {raw_data}")
    rd_split = raw_data.split("Get directions")
    address = rd_split[0]
    address = remove_comma(address)
    logger.info(f"Clean Address: {address}")
    hoo = rd_split[1].split("Restaurant")[0].split(":,")[-1]
    hoo = remove_comma(hoo)
    logger.info(f"HOO: {hoo}")
    return address, hoo


def fetch_records_qa(sgw: SgWriter):
    qa_store_locator_url = "https://www.ikea.com/qa/en/stores/"
    r1 = get_response(qa_store_locator_url)
    sel1 = html.fromstring(r1.text, "lxml")
    xpath_store_locator = '//div[contains(@tabindex, "-1")]/a/@href'
    page_urls = sel1.xpath(xpath_store_locator)
    logger.info(f"page urls: {page_urls}")
    for page_url in page_urls:
        logger.info(f"Pulling the data from {page_url}")
        r2 = get_response(page_url)
        sel2 = html.fromstring(r2.text, "lxml")
        xpath_locname = '//meta[contains(@property, "og:title")]/@content'
        location_name = "".join(sel2.xpath(xpath_locname))
        logger.info(f"Location Name: {location_name}")
        xpath_address = (
            '//div[*[strong[contains(text(), "IKEA Doha store")]]]/p//text()'
        )

        address_custom = sel2.xpath(xpath_address)
        address1, hoo = get_add_n_hoo_qa(address_custom)
        logger.info(f"Address: {address1}")
        street_address, city, state, zip_postal = get_parsed_address(address1)

        xpath_gmap_url1 = '//p[a[contains(text(), "Get directions")]]/a/@href'
        xpath_gmap_url2 = '//a[*[*[contains(text(), "Get directions")]]]/@href'
        xpath_gmap_url = f"{xpath_gmap_url1} | {xpath_gmap_url2}"
        gurl = sel2.xpath(xpath_gmap_url)
        logger.info(f"Google URL List: {gurl}")
        try:
            gurl = gurl[0]
            gurl_redirected = ""
            if gurl:
                logger.info(f"Google URL: {gurl}")
                r3 = get_response(gurl)
                logger.info(f"Google URL Response HTTP Status Code: {r3.status_code}")
                gurl_redirected = r3.url
                logger.info(f"gurl: {gurl_redirected}")
            lat, lng = get_latlng(str(gurl_redirected))
        except:
            lat = MISSING
            lng = MISSING

        logger.info(f"HOO: {hoo}")
        rec = SgRecord(
            locator_domain=get_domain(page_url),
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=get_country_code(page_url),
            store_number=MISSING,
            phone=get_phone(sel2),
            location_type=MISSING,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hoo if hoo else MISSING,
            raw_address=address1 if address1 else MISSING,
        )
        logger.info(
            f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
        )
        sgw.write_row(rec)


# 13 - Serbia (RS)
def fetch_records_rs(sgw: SgWriter):
    rs_store_locator_url = "https://www.ikea.com/rs/sr/stores/"
    r = get_response(rs_store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    page_url = rs_store_locator_url
    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    location_name = sel.xpath(xpath_locname)[0]
    logger.info(f"Location Name: {location_name}")

    xpath_address = '//*[*[*[contains(text(), "Adresa")]]]/p/text()'
    at = sel.xpath(xpath_address)
    address1 = " ".join(at)
    logger.info(f"Address: {address1}")
    street_address, city, state, zip_postal = get_parsed_address(address1)

    xpath_phone = '//a[contains(@href, "tel:")]/@href'
    ph = sel.xpath(xpath_phone)[0].replace("tel:", "")
    phone = ph.strip() if ph else MISSING

    xpath_gmap_url1 = '//a[*[*[contains(text(), "Get directions")]]]/@href'
    xpath_gmap_url2 = '//a[contains(@href, "https://www.google.com/maps")]/@href'
    xpath_gmap_url12 = f"{xpath_gmap_url1} | {xpath_gmap_url2}"
    xpath_gmap_url = '//div[contains(@class, "google-maps-link")]/a/@href'
    gurl = sel.xpath(xpath_gmap_url)
    lat = ""
    lng = ""
    if gurl:
        gurl = gurl[0]
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
    else:
        lat = MISSING
        lng = MISSING
    xpath_hours = '//*[*[*[contains(text(), "Radno vreme:")]]]/p/text()'
    hours = sel.xpath(xpath_hours)
    hoo = " ".join(hours).strip()
    logger.info(f"HOO: {hoo}")
    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hoo if hoo else MISSING,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


# 14 - Slovakia (SK)
def fetch_records_sk(sgw: SgWriter):
    sk_store_locator_url = "https://www.ikea.com/sk/sk/stores/bratislava/"
    r = get_response(sk_store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    page_url = sk_store_locator_url
    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    location_name = sel.xpath(xpath_locname)[0]
    logger.info(f"Location Name: {location_name}")

    xpath_address_sk = '//*[*[contains(text(), "Adresa")]]/p/text()'
    at = sel.xpath(xpath_address_sk)
    address1 = " ".join(at)
    logger.info(f"Address: {address1}")
    street_address, city, state, zip_postal = get_parsed_address(address1)
    xpath_phone = '//*[contains(text(), "+421")]/text()'
    ph = sel.xpath(xpath_phone)[0].replace("tel:", "")
    phone = ph.strip() if ph else MISSING

    # Zobraziť na mape
    xpath_gmap_url = '//a[contains(text(), "Zobraziť na mape")]/@href'
    gurl = sel.xpath(xpath_gmap_url)
    lat = ""
    lng = ""
    try:
        gurl = gurl[0]
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
    except:
        lat = MISSING
        lng = MISSING

    xpath_hours = '//div[*[contains(text(), "Otváracie hodiny")]]/p/text()'
    hours = sel.xpath(xpath_hours)[0]
    hoo = hours.strip()
    hours_of_operation = hoo if hoo else MISSING
    logger.info(f"HOO: {hours_of_operation}")

    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


# 15 - Slovenia


def fetch_records_si(sgw: SgWriter):
    si_store_locator_url = "https://www.ikea.com/si/sl/stores/"
    r = get_response(si_store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    page_url = si_store_locator_url
    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    location_name = sel.xpath(xpath_locname)[0]
    logger.info(f"Location Name: {location_name}")
    xpath_address = '//*[*[contains(text(), "Naslov")]]/p/text()'
    # Naslov ( Address )
    at = sel.xpath(xpath_address)
    address1 = " ".join(at)
    logger.info(f"Address: {address1}")
    street_address, city, state, zip_postal = get_parsed_address(address1)
    xpath_phone = '//a[contains(@href, "tel:")]/@href'
    xpath_phone = (
        '//*[contains(text(), "+421")]/text() | //a[contains(@href, "tel:")]/@href'
    )
    ph = sel.xpath(xpath_phone)[0].replace("tel:", "")
    phone = ph.strip() if ph else MISSING
    xpath_gmap_url = '//a[contains(text(), "Zobraziť na mape")]/@href'
    gurl = sel.xpath(xpath_gmap_url)
    lat = ""
    lng = ""
    try:
        gurl = gurl[0]
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
    except:
        lat = MISSING
        lng = MISSING

    xpath_hours = '//div[*[contains(text(), "Obratovalni čas")]]/p/text()'
    # Obratovalni čas
    hours = sel.xpath(xpath_hours)[0]
    hoo = hours.strip()
    hours_of_operation = hoo if hoo else MISSING
    logger.info(f"HOO: {hours_of_operation}")
    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


# 16 - Ukraine (UA)
def fetch_records_ua(sgw: SgWriter):
    ua_store_locator_url = "https://www.ikea.com/ua/uk/stores/"
    r = get_response(ua_store_locator_url)
    sel = html.fromstring(r.text, "lxml")
    page_url = ua_store_locator_url
    xpath_locname = '//meta[contains(@property, "og:title")]/@content'
    location_name = sel.xpath(xpath_locname)[0]
    logger.info(f"Location Name: {location_name}")
    xpath_address = '//*[*[*[contains(text(), "Адреса")]]]/p/text()'
    at = sel.xpath(xpath_address)[1:]
    address1 = " ".join(at)
    logger.info(f"Address: {address1}")
    street_address, city, state, zip_postal = get_parsed_address(address1)
    xpath_phone = '//a[contains(@href, "tel:")]/@href'
    xpath_phone = (
        '//*[contains(text(), "+421")]/text() | //a[contains(@href, "tel:")]/@href'
    )
    phone = ""
    try:
        ph = sel.xpath(xpath_phone)[0].replace("tel:", "")
        phone = ph.strip()
    except:
        phone = MISSING

    # Get directions - Прокласти маршрут
    xpath_gmap_url = '//a[contains(text(), "Прокласти маршрут")]/@href'
    gurl = sel.xpath(xpath_gmap_url)
    lat = ""
    lng = ""
    try:
        gurl = gurl[0]
        r3 = get_response(gurl)
        gurl_redirected = r3.url
        logger.info(f"gurl: {gurl_redirected}")
        lat, lng = get_latlng(str(gurl_redirected))
    except:
        lat = MISSING
        lng = MISSING
    # Work Schedule - Графік роботи
    xpath_hours = '//div[*[*[contains(text(), "Графік роботи")]]]/p/text()'
    hoo = " ".join(sel.xpath(xpath_hours))
    hours_of_operation = hoo if hoo else MISSING
    logger.info(f"HOO: {hours_of_operation}")
    rec = SgRecord(
        locator_domain=get_domain(page_url),
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=zip_postal,
        country_code=get_country_code(page_url),
        store_number=MISSING,
        phone=phone,
        location_type=MISSING,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours_of_operation,
        raw_address=address1 if address1 else MISSING,
    )
    logger.info(
        f"Record for {rec.country_code()} | {rec.page_url()}\n{rec.as_dict()}\n"
    )
    sgw.write_row(rec)


def fetch_data(sgw: SgWriter):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_bh = [executor.submit(fetch_records_bh, sgw)]
        tasks.extend(task_bh)

        task_bg = [executor.submit(fetch_records_bg, sgw)]
        tasks.extend(task_bg)

        task_hr = [executor.submit(fetch_records_hr, sgw)]
        tasks.extend(task_hr)

        task_cy = [executor.submit(fetch_records_cy, sgw)]
        tasks.extend(task_cy)

        task_in = [executor.submit(fetch_records_in, sgw)]
        tasks.extend(task_in)

        task_ie = [executor.submit(fetch_records_ie, sgw)]
        tasks.extend(task_ie)

        task_jo = [executor.submit(fetch_records_jo, sgw)]
        tasks.extend(task_jo)

        task_kw = [executor.submit(fetch_records_kw, sgw)]
        tasks.extend(task_kw)

        task_mx = [executor.submit(fetch_records_mx, sgw)]
        tasks.extend(task_mx)

        task_ma = [executor.submit(fetch_records_ma, sgw)]
        tasks.extend(task_ma)

        task_pr = [executor.submit(fetch_records_pr, sgw)]
        tasks.extend(task_pr)

        task_rs = [executor.submit(fetch_records_rs, sgw)]
        tasks.extend(task_rs)

        task_sk = [executor.submit(fetch_records_sk, sgw)]
        tasks.extend(task_sk)

        task_si = [executor.submit(fetch_records_si, sgw)]
        tasks.extend(task_si)

        task_ua = [executor.submit(fetch_records_ua, sgw)]
        tasks.extend(task_ua)

        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Started")
    logger.info(f"Total Countries to be crawled: {len(store_locator_list)}")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

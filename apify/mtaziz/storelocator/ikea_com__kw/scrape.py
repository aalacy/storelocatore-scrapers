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


def get_response_gmapurl(url):
    with SgRequests(verify_ssl=False) as http:
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


# Kuwait - Please a separate ticket


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


# Qatar
def remove_comma(d):
    c = d.strip().lstrip(",").rstrip(",").strip().lstrip(";").rstrip(";").lstrip(":")
    return c


# Kuwait


def fetch_records_kw(sgw: SgWriter):
    kw_store_locator_url = "https://www.ikea.com/kw/en/stores/"
    try:
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
            gurl_list = sel2.xpath(xpath_gmap_url)
            logger.info(f"Google Get Directions URL (KW): {gurl_list}")

            gurl = gurl_list[idx]
            lat = ""
            lng = ""
            try:
                session = SgRequests()
                r3 = session.get(gurl)
                gurl_redirected = r3.url
                logger.info(f"gurl: {gurl_redirected}")
                lat, lng = get_latlng(str(gurl_redirected))
            except:
                lat = MISSING
                lng = MISSING

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
    except Exception as e:
        logger.info(f"Please Fix FetchRecordsKW: << {e} >> for {kw_store_locator_url}")


def fetch_data(sgw: SgWriter):
    # NOTE: Kuwait will have a separate ticket as
    # it is having issues Google Map URls
    # 502 ProxyError.

    # [0]: https://www.ikea.com/bh/en/stores Bahrain BH
    # [1]: https://www.ikea.bg/stores/ Bulgaria BG
    # [2]: https://www.ikea.com/hr/hr/stores Croatia HR
    # [3]: https://www.ikea.com.cy/katastimata/ Cyprus CY
    # [4]: https://www.ikea.com/in/en/stores/ India IN
    # [5]: https://www.ikea.com/ie/en/stores/ Ireland IE
    # [6]: https://www.ikea.com/jo/en/stores Jordan JO
    # [7]: https://www.ikea.com/kw/en/stores/ Kuwait KW
    # [8]: https://www.ikea.com/mx/en/stores/ Mexico MX
    # [9]: https://www.ikea.com/ma/en/stores/ Morocco MA
    # [10]: https://www.ikea.pr/mayaguez/en/information/contact Puerto Rico PR
    # [11]: https://www.ikea.com/qa/en/stores/doha/ Qatar QA
    # [12]: https://www.ikea.com/rs/sr/stores/ Serbia RS
    # [13]: https://www.ikea.com/sk/sk/stores/ Slovakia SK
    # [14]: https://www.ikea.com/si/sl/stores/ Slovenia SI
    # [15]: https://www.ikea.com/ua/uk/stores/ Ukraine UA

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_kw = [executor.submit(fetch_records_kw, sgw)]
        tasks.extend(task_kw)
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

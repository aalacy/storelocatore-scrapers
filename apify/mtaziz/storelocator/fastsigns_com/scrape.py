from collections import OrderedDict
from sgrequests import SgRequests
from sgselenium import SgChrome
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
import json
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

logger = SgLogSetup().get_logger("fastsigns_com")
url_locations = "https://www.fastsigns.com/locations"
DOMAIN = "https://www.fastsigns.com"
MISSING = "<MISSING>"


headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "accept": "application/json",
}

session = SgRequests()


def get_data_from_3_different_sources(puuc, idx):

    data_src = OrderedDict()
    page_url_usca = puuc
    logger.info(f"Pulling the data from {idx}: {page_url_usca}")
    r_app_json = session.get(puuc, headers=headers, timeout=120)
    data_app_json = html.fromstring(r_app_json.text, "lxml")

    # Data from source 1
    xpath_script_app_ld_json = (
        '//script[@type="application/ld+json" and contains(text(), "context")]/text()'
    )
    data_script_app_ld_json = data_app_json.xpath(xpath_script_app_ld_json)

    # Data from source 2
    data_from_cookievalue = data_app_json.xpath(
        '//div[input[@id="CookieValue"]]/input/@value'
    )
    if data_script_app_ld_json:
        logger.info(f"Data from script application/ld+json: {data_script_app_ld_json}")
        data_script_app_ld_json = "".join(data_script_app_ld_json)
        data_from_script = data_script_app_ld_json.replace("} ]", "")
        dfs = data_from_script.rstrip("\n").split(",")
        dfs2 = [" ".join(i.split()) for i in dfs]
        dfs3 = ",".join(dfs2)
        data_json = json.loads(dfs3.replace("},}", "}}"))
        data_script_src1 = {"data_src_script1": data_json}

    else:
        data_script_src1 = {"data_src_script1": ""}
    if data_from_cookievalue:
        data_from_cookievalue1 = (
            " ".join(data_from_cookievalue)
            .replace("%20", " ")
            .replace("CurrCenterInfo", "")
            .replace("%c2%ae", "")
        )
        logger.info(f"data from cookievalue: {data_from_cookievalue1}")
        data_from_cookievalue2 = json.loads(data_from_cookievalue1)
        data_cookie_src2 = {"data_src_cookie2": data_from_cookievalue2}
    else:
        data_cookie_src2 = {"data_src_cookie2": ""}

    # Data From Page Source 3
    xpath_phone = '//ul[@class="location-info"]/li/span[contains(text(), "P:")]/text()'
    phone_psrc = "".join(data_app_json.xpath(xpath_phone)).replace("P:", "").strip()
    logger.info(f"Phone from Page Src: {phone_psrc}")
    xpath_hoo = '//ul[@class="location-info"]/li[5]//text()'
    hoo_psrc = data_app_json.xpath(xpath_hoo)
    hoo_psrc = [" ".join(i.split()) for i in hoo_psrc]
    hoo_psrc = [i.replace("|", "") for i in hoo_psrc]
    hoo_psrc = [i for i in hoo_psrc if i]
    hoo_psrc = "; ".join(hoo_psrc)
    logger.info(f"HOO from Page Src: {hoo_psrc}")

    xpath_st = '//ul[@class="location-info"]/li[2]//text()'
    st_pagesrc = data_app_json.xpath(xpath_st)
    st_pagesrc = [" ".join(i.split()) for i in st_pagesrc]
    st_pagesrc = [i for i in st_pagesrc if i]
    if st_pagesrc:
        street_address3 = st_pagesrc[0]
        city3 = st_pagesrc[-1].split(",")[0]
        state3 = st_pagesrc[-1].split(",")[-1].strip().split(" ")[0]
        zip_postal3 = st_pagesrc[-1].split(",")[-1].strip().split(" ")[1:]
        zip_postal3 = " ".join(zip_postal3)
    else:
        street_address3 = ""
        city3 = ""
        state3 = ""
        zip_postal3 = ""

    xpath_latlng = '//a[contains(@href, "https://www.google.com/maps/dir/Current+Location/")]/@href'
    latlng_from_google_url = data_app_json.xpath(xpath_latlng)
    if latlng_from_google_url:
        latlng = "".join(latlng_from_google_url)
        latlng = latlng.split("https://www.google.com/maps/dir/Current+Location/")[-1]
        lat3 = latlng.split(",")[0]
        lng3 = latlng.split(",")[-1]
        logger.info(f"latlng from Google URL: Latitude: {lat3} | Longitude: {lng3} ")
    else:
        lat3 = ""
        lng3 = ""
    # Location Name
    xpath_location_name3 = '//ul[@class="location-info"]/li[1]//text()'
    location_name3 = data_app_json.xpath(xpath_location_name3)
    location_name3 = [i.replace("®", "").strip() for i in location_name3]
    location_name3 = [i for i in location_name3 if i]
    location_name3 = " of ".join(location_name3)

    data_page_src3 = {
        "data_page_src3": {
            "location_name3": location_name3,
            "hoo": hoo_psrc,
            "phone": phone_psrc,
            "street_address3": street_address3,
            "city3": city3,
            "state3": state3,
            "zip_postal3": zip_postal3,
            "lat3": lat3,
            "lng3": lng3,
        }
    }
    page_url_and_id = {"purl": puuc, "id": idx}
    data_src.update(data_script_src1)
    data_src.update(data_cookie_src2)
    data_src.update(data_page_src3)
    data_src.update(page_url_and_id)
    return data_src


def get_page_urls_and_country_codes():
    with SgChrome(is_headless=True) as driver:
        driver.get("https://www.fastsigns.com/worldwide")
        xpath_data_table = "//select[@name='DataTables_Table_0_length']/option[5]"
        time.sleep(20)
        WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, xpath_data_table))
        )
        driver.find_element_by_xpath(xpath_data_table).click()
        time.sleep(5)
        logger.info("Please wait until page fully loaded")
        data_raw = html.fromstring(driver.page_source, "lxml")
        logger.info("Page Successfully Loaded")

    xpath_trs = '//table[@id="DataTables_Table_0"]/tbody/tr'
    trs = data_raw.xpath(xpath_trs)
    page_urls_and_countries = []
    for tr in trs:
        # Location Name
        locname = "".join(tr.xpath('./td[@class="sorting_1"]//text()'))
        locname = " ".join(locname.split())
        locname = locname.strip().replace("®", "").strip()
        coming_soon = tr.xpath('./td[@class="sorting_1"]/span/text()')
        if coming_soon:
            continue

        page_url = "".join(tr.xpath('./td[@class="sorting_1"]/a/@href'))
        page_url = "".join(page_url)
        country = "".join(tr.xpath("./td[5]/text()"))
        locname_lower = locname.lower()
        if country == "CA" or country == "US" and "coming soon" not in locname_lower:
            if "https://www.fastsigns.com/" not in page_url:
                page_url_us_or_ca = f"{'https://www.fastsigns.com'}{page_url}"
            else:
                page_url_us_or_ca = f"{page_url}"
            page_urls_and_countries.append((page_url_us_or_ca, country))
    return page_urls_and_countries


def fetch_data():
    urls_countries_list = get_page_urls_and_country_codes()
    for idx, u in enumerate(urls_countries_list):
        page_url = u[0]
        locator_domain = DOMAIN
        data = get_data_from_3_different_sources(page_url, idx)
        logger.info(f"Data from different Sources: {data} ")
        if data["data_page_src3"]:
            location_name3 = data["data_page_src3"]["location_name3"]
            street_address3 = data["data_page_src3"]["street_address3"]
            city3 = data["data_page_src3"]["city3"]
            state3 = data["data_page_src3"]["state3"]
            zip_postal3 = data["data_page_src3"]["zip_postal3"]
            phone3 = data["data_page_src3"]["phone"]
            lat3 = data["data_page_src3"]["lat3"]
            lng3 = data["data_page_src3"]["lng3"]
            hoo3 = data["data_page_src3"]["hoo"]
        else:
            location_name3 = ""
            street_address3 = ""
            city3 = ""
            state3 = ""
            zip_postal3 = ""
            phone3 = ""
            lat3 = ""
            lng3 = ""
            hoo3 = ""

        if "https://www.fastsigns.com/82-yorktown-va" in page_url:
            continue
        location_name = location_name3 if location_name3 else MISSING
        street_address = street_address3 if street_address3 else MISSING
        city = city3 if city3 else MISSING
        state = state3 if state3 else MISSING
        zip_postal = zip_postal3 if zip_postal3 else MISSING
        country_code = u[1] if u[1] else MISSING
        store_number = ""
        try:
            store_number = page_url.split("/")[-1].split("-")[0]
        except:
            store_number = MISSING
        phone = phone3 if phone3 else MISSING
        # Location Type
        location_type = ""
        if data["data_src_script1"]:
            location_type = data["data_src_script1"]["@type"]
        else:
            location_type = MISSING
        logger.info(f"Location Type: {location_type}")

        latitude = lat3 if lat3 else MISSING
        longitude = lng3 if lng3 else MISSING
        hours_of_operation = hoo3 if hoo3 else MISSING
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


# If SgRecord Used


def scrape():
    logger.info("Started")
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

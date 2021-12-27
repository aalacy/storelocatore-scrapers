import re
import json
from urllib.parse import urljoin
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sglogging import SgLogSetup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ssl
from lxml import html
from sgpostal.sgpostal import parse_address_intl


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


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
start_url = "https://www.worldwidegolfshops.com/roger-dunn-golf-shops"
logger = SgLogSetup().get_logger("worldwidegolfshops_com__vans-golf-shops_aspx")
MISSING = SgRecord.MISSING


def get_store_urls():
    xpath_meta = '//meta[@name="country"]'
    driver = get_driver(start_url, xpath_meta)
    sel = html.fromstring(driver.page_source, "lxml")
    data = sel.xpath('//script[contains(text(), "store.custom.find-a-store")]/text()')[
        2
    ]
    data = json.loads(data)
    all_poi_raw = []
    for k, v in data.items():
        if "text" in k:
            all_poi_raw.append(v)
    s = set()
    all_locations = []
    for poi in all_poi_raw:
        if poi["props"].get("text"):
            try:
                links_raw = poi["props"]["text"].split("](")[1].split(")\n")[0]
                if "/store/roger-dunn" in links_raw or "rdgolfhi.com" in links_raw:
                    if links_raw not in s:
                        all_locations.append(links_raw)
                    s.add(links_raw)
            except Exception:
                continue
    return all_locations


def get_driver(url, xpath, driver=None):
    if driver is not None:
        driver.quit()
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=USER_AGENT,
                is_headless=True,
            ).driver()
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(((By.XPATH, xpath)))
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


def get_phone(sel, page_url):
    # Phone
    phone = ""
    try:
        phone_xpath1 = '//p[strong[contains(text(), "Phone")]]//text()'
        phone_xpath2 = (
            '//p[strong[contains(text(), "Phone")]]/following-sibling::p//text()'
        )
        phone = sel.xpath(f"{phone_xpath1} | {phone_xpath2}")
        phone = [i.replace("Phone", "") for i in phone]
        phone = [i for i in phone if i]
        if not phone:
            phone = MISSING
        phone = "".join(phone)
        logger.info(f"Phone: {phone}")
        return phone
    except Exception as e:
        logger.info(f"Fix Issue with {e} | {page_url}")


def get_hoo(sel, page_url):
    hours_of_operation = ""
    try:
        hours = sel.xpath(
            '//p[strong[contains(text(), "HOURS")]]/text() | //p[strong[contains(text(), "HOURS")]]/following-sibling::p/text()'
        )
        hours = hours[:-1]
        hours = [" ".join(i.split()) for i in hours]
        if hours:
            hours_of_operation = "; ".join(hours)
        else:
            hours_of_operation = MISSING

        logger.info(f"HOO: {hours_of_operation}")
        return hours_of_operation
    except Exception as e:
        logger.info(f"Fix Issue with {e} | {page_url}")


def get_data_from_rdgolfhi_com(page_url):
    with SgRequests() as http:
        r3 = http.get(page_url, "lxml")
        sel3 = html.fromstring(r3.text, "lxml")
        d3 = sel3.xpath("//div/@data-block-json")[0]
        d3 = json.loads(d3)
        logger.info(f"d3: {d3}")
        hours = sel3.xpath('//p[strong[contains(text(), "HOURS")]]/text()')
        hours = "".join(hours)
        domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
        phone = get_phone(sel3, page_url)

        # Hours of Operation
        hours_of_operation = get_hoo(sel3, page_url)

        # Address
        dloc = d3["location"]
        country_code = dloc["addressCountry"]
        if "United States" in country_code:
            country_code = "US"
        dloc = d3["location"]
        city_s_zc = dloc["addressLine2"]
        pai = parse_address_intl(city_s_zc)
        city = pai.city if pai.city else MISSING
        state = pai.state if pai.state else MISSING
        zip_postal = pai.postcode if pai.postcode else MISSING
        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=dloc["addressTitle"] or MISSING,
            street_address=dloc["addressLine1"] or MISSING,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=MISSING,
            phone=phone,
            location_type="SportingGoodsStore",
            latitude=dloc["mapLat"] or MISSING,
            longitude=dloc["mapLng"] or MISSING,
            hours_of_operation=hours_of_operation,
        )
        yield item


def fetch_data():
    all_locations = get_store_urls()
    for idx, url in enumerate(all_locations[0:]):
        domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
        if "https://" not in url:
            page_url = urljoin(start_url, url)
            logger.info(f"Pulling the data from {page_url}")
            xpath_store_hours = '//div[contains(text(), "STORE HOURS")]'
            if "##" in page_url:
                continue
            driver = get_driver(page_url, xpath_store_hours)
            loc_dom = html.fromstring(driver.page_source, "lxml")
            poi = loc_dom.xpath('//script[contains(text(), "address")]/text()')[0]
            poi = json.loads(poi)
            location_name = "".join(loc_dom.xpath("//title/text()"))
            logger.info(f"[{idx}] Location Name: {location_name}")
            hoo = []
            try:
                for e in poi["openingHoursSpecification"]:
                    if not e.get("dayOfWeek"):
                        continue
                    hoo.append(f'{e["dayOfWeek"]} {e["opens"]} {e["closes"]}')
            except Exception as e:
                logger.info(f" [ {e} ] Please fix it at >>> [{idx}] | {page_url}")
            hours_of_operation = " ".join(hoo)
            country_code = ""
            country_code = "US"
            if "store/the-golf-mart-nm-87111/ABQ" in page_url:
                country_code = "MX"

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=location_name,
                street_address=poi["address"]["streetAddress"],
                city=poi["address"]["addressLocality"],
                state=poi["address"]["addressRegion"],
                zip_postal=poi["address"]["postalCode"],
                country_code=country_code,
                store_number=MISSING,
                phone=poi["telephone"],
                location_type=poi["@type"][0],
                latitude=poi["geo"]["latitude"],
                longitude=poi["geo"]["longitude"],
                hours_of_operation=hours_of_operation,
            )

            yield item
        else:
            yield from get_data_from_rdgolfhi_com(url)


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()

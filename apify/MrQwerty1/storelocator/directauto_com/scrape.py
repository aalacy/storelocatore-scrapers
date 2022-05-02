from lxml import html
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgselenium import SgChrome
from selenium.webdriver.common.by import By
from sglogging import sglog
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context

logger = sglog.SgLogSetup().get_logger(logger_name="directauto.com")

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)

sitemap = "https://local.directauto.com/sitemap.xml"


def get_urls():
    with SgChrome(user_agent=user_agent) as driver:
        driver.get(sitemap)
        tree = html.fromstring(driver.page_source, "lxml")
        links = tree.xpath("//loc/text()")
        urls = set()
        for link in links:
            if link.count("/") == 5:
                urls.add(f"{link}.json")

    return urls


def get_data(api, sgw: SgWriter):
    with SgChrome(user_agent=user_agent) as driver:
        logger.info(f"Crawling {api}")
        driver.get(api)
        try:
            j = json.loads(driver.find_element(By.CSS_SELECTOR, "body").text)["profile"]
        except Exception as e:
            logger.info(f"{api} raised the error: {e}")
            return
        page_url = api.replace(".json", "")
        location_name = j.get("name")
        logger.info(f"Location Name: {location_name}")
        a = j.get("address") or {}
        adr1 = a.get("line1") or ""
        adr2 = a.get("line2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("region")
        postal = a.get("postalCode")

        try:
            phone = j["mainPhone"]["display"]
        except:
            phone = SgRecord.MISSING
        g = j.get("yextDisplayCoordinate") or {}
        latitude = g.get("lat")
        longitude = g.get("long")

        _tmp = []
        try:
            hours = j["hours"]["normalHours"]
        except:
            hours = []

        for h in hours:
            day = h.get("day")
            isclosed = h.get("isClosed")
            if isclosed:
                _tmp.append(f"{day}: Closed")
                continue

            try:
                i = h.get("intervals")[0]
            except:
                i = dict()

            start = str(i.get("start")).zfill(4)
            end = str(i.get("end")).zfill(4)
            start = start[:2] + ":" + start[2:]
            end = end[:2] + ":" + end[2:]
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    logger.info(f"Total pages to crawl {len(urls)}")
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://directauto.com/"

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

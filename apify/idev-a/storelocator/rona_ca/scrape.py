from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
import re
import demjson
from sgselenium import SgFirefox
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rona")

_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def _valid(val):
    return (
        val.strip()
        .replace("–", "-")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\\\u00E9", "e")
        .replace("\\xa0\\xa", " ")
        .replace("\\xa0", " ")
        .replace("\\xa", " ")
        .replace("\\xae", "")
    )


def _script(val):
    return (
        val.strip()
        .replace("\r", "")
        .replace("\n", "")
        .replace("\t", "")
        .encode("unicode-escape")
        .decode("utf8")
        .replace("\\\\u00E9", "e")
        .replace("\\'", "###")
        .replace("'", '"')
        .replace("\\\\", "")
        .replace("/", "")
        .replace("\\", "")
    )


days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
locator_domain = "https://www.rona.ca/"


def _detail(page_url, driver):
    soup2 = bs(driver.page_source, "lxml")
    block = soup2.select_one("div.visible-xs div.storedetails__address-block")
    hours_of_operation = "; ".join(
        [
            _["datetime"]
            for _ in soup2.select(
                ".visible-xs #mainHours ul.storedetails__list.storedetails__list-hours li time"
            )
        ]
    )
    script1 = (
        soup2.find("script", string=re.compile("var _storeDetails ="))
        .string.split("var _storeDetails =")[1]
        .strip()[:-1]
    )
    store_detail = demjson.decode(script1)
    return SgRecord(
        page_url=page_url,
        store_number=store_detail["id"],
        location_name=block.select_one('[itemprop="name"]').text,
        street_address=block.select_one('[itemprop="streetAddress"]').text,
        city=block.select_one('[itemprop="addressLocality"]').text,
        state=block.select_one('[itemprop="addressRegion"]').text,
        zip_postal=block.select_one('[itemprop="postalCode"]').text,
        country_code="CA",
        latitude=soup2.select_one('meta[itemprop="latitude"]')["content"],
        longitude=soup2.select_one('meta[itemprop="longitude"]')["content"],
        phone=block.select_one("div.phone").text.replace("Phone: ", ""),
        locator_domain=locator_domain,
        hours_of_operation=_valid(hours_of_operation),
    )


def fetch_data():
    with SgFirefox() as driver:
        total = 0
        base_url = "https://www.rona.ca/sitemap-stores-en.xml"
        driver.get(base_url)
        soup = bs(driver.page_source, "lxml")
        urls = soup.select("loc")
        logger.info(f"{len(urls)} urls found")
        for url in urls:
            page_url = url.text.strip()
            try:
                driver.get(page_url)
            except:
                continue
            total += 1
            logger.info(f"[total {total}] {page_url}")
            yield _detail(page_url, driver)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

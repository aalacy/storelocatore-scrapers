from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import demjson
from sgselenium import SgFirefox
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("rona")

_headers = {
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
missing_urls = []


def _detail(marker, page_url, driver):
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
        latitude=marker["la"],
        longitude=marker["ln"],
        phone=block.select_one("div.phone").text.replace("Phone: ", ""),
        locator_domain=locator_domain,
        hours_of_operation=_valid(hours_of_operation),
    )


def fetch_data():
    with SgRequests() as session:
        with SgFirefox() as driver:
            total = 0
            base_url = "https://www.rona.ca/webapp/wcs/stores/servlet/RonaStoreListDisplay?storeLocAddress=toronto&storeId=10151&catalogId=10051&langId=-1&latitude=43.653226&longitude=-79.3831843"
            soup = bs(session.get(base_url, headers=_headers).text, "lxml")
            script = _script(
                soup.find("script", string=re.compile("var storeMarkers = ")).string
            )
            temp = (
                script.split("var storeMarkers = ")[1][:-1]
                .replace("\\'", "###")
                .replace("'", '"')
                .replace("\\\\", "")
                .replace("/", "")
                .replace("\\", "")
            )
            markers = json.loads(temp)
            logger.info(f"{len(markers)} found")
            for marker in markers:
                marker_url = f"https://www.rona.ca/webapp/wcs/stores/servlet/RonaStoreDetailAjax?catalogId=10051&langId=-1&storeId=10151&id={marker['id']}"
                soup1 = bs(session.get(marker_url, headers=_headers).text, "lxml")
                page_url = soup1.select_one("a.detail")["href"]
                try:
                    driver.get(page_url)
                except:
                    missing_urls.append(dict(page_url=page_url, marker=marker))
                    driver.delete_all_cookies()
                    continue
                total += 1
                logger.info(f"[total {total}] {page_url}")
                yield _detail(marker, page_url, driver)

            for url in missing_urls:
                try:
                    driver.get(url["page_url"])
                except:
                    missing_urls.append(
                        dict(page_url=url["page_url"], marker=url["marker"])
                    )
                    driver.delete_all_cookies()
                    continue
                total += 1
                logger.info(f"[total {total}] {url['page_url']}")
                yield _detail(url["marker"], url["page_url"], driver)


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

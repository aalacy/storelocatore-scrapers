import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger("")

locator_domain = "https://www.specsavers.co.uk"
base_url = "https://www.specsavers.co.uk/stores/full-store-list"

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


max_workers = 1


def fetchConcurrentSingle(link):
    page_url = "https://www.specsavers.co.uk/stores/" + link["href"]
    logger.info(page_url)
    res = request_with_retries(page_url)
    if res.status_code == 200:
        soup = bs(res.text, "lxml")
        location_type = "Hearing Centre" if "hearing" in page_url else "Optician"
        try:
            addr = list(soup.select_one("div.store p").stripped_strings)
        except:
            addr = (
                soup.select_one("a#contact-info_location-text").text.strip().split(",")
            )
        return page_url, res, soup, location_type, addr


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            if result:
                count = count + 1
                if count % reminder == 0:
                    logger.debug(f"Concurrent Operation count = {count}")
                output.append(result)
    return output


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        store_links = soup.select("div.item-list ul li a")
        for page_url, res, soup, location_type, addr in fetchConcurrentList(
            store_links
        ):
            try:
                detail_url = soup.find(
                    "script", src=re.compile(r"https://knowledgetags.yextpages.net")
                )["src"].replace("&amp;", "&")
                res2 = session.get(detail_url)
                _ = json.loads(res2.text.split("Yext._embed(")[1].strip()[:-1])[
                    "entities"
                ][0]["attributes"]
                if _.get("yextDisplayLat"):
                    latitude = _["yextDisplayLat"]
                    longitude = _["yextDisplayLng"]
                else:
                    latitude = _["displayLat"]
                    longitude = _["displayLng"]
                yield SgRecord(
                    page_url=page_url,
                    location_name=_["name"],
                    street_address=_["address"],
                    city=_["city"],
                    state=_.get("state"),
                    zip_postal=_["zip"],
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation="; ".join(_.get("hours", [])),
                    location_type=location_type,
                    country_code=_["countryCode"],
                    raw_address=" ".join(addr).replace("\n", "").replace("\r", ""),
                )
            except:
                with SgChrome() as driver:
                    driver.get(page_url)
                    res = driver.page_source
                    soup = bs(res, "lxml")
                    location_type = (
                        "Hearing Centre" if "hearing" in page_url else "Optician"
                    )
                    addr = list(soup.select_one("div.store p").stripped_strings)
                    street_address = " ".join(addr[:-3])
                    if street_address.endswith(","):
                        street_address = street_address[:-1]
                    try:
                        coord = json.loads(
                            res.text.split("var position =")[1].split(";")[0]
                        )
                    except:
                        coord = {"lat": "", "lng": ""}
                    hours = [
                        tr["content"]
                        for tr in soup.select("table.opening--day-and-time tr")
                    ]
                    try:
                        location_name = soup.select_one(
                            "h1.store-header--title"
                        ).text.strip()
                    except:
                        location_name = soup.select_one(
                            "h1.general-information__store-name"
                        ).text.strip()
                    yield SgRecord(
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=addr[-3].replace(",", ""),
                        state=addr[-2].replace(",", ""),
                        zip_postal=addr[-1].replace(",", ""),
                        phone=soup.select_one(
                            "span.contact--store-telephone--text"
                        ).text.strip(),
                        locator_domain=locator_domain,
                        latitude=coord.get("lat"),
                        longitude=coord.get("lng"),
                        hours_of_operation="; ".join(hours),
                        location_type=location_type,
                        country_code="UK",
                        raw_address=" ".join(addr).replace("\n", "").replace("\r", ""),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

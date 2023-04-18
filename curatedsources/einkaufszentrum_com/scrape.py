from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import math
import re
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.einkaufszentrum.com"
base_url = "https://www.einkaufszentrum.com/?limitstart={}"
max_workers = 8


def fetchConcurrentSingle(page_url):
    response = request_with_retries(page_url)
    return page_url, bs(response.text, "lxml")


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
    with SgRequests() as session:
        page = 0
        urls = []
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            locations = soup.select("div.reindex_address_item")
            if not locations:
                break
            page += 10
            logger.info(f"{page}, {len(locations)}")
            for _ in locations:
                if not _.h4:
                    continue
                urls.append(locator_domain + _.a["href"])

        for page_url, sp1 in fetchConcurrentList(urls):
            logger.info(page_url)
            hours = [
                ": ".join(hh.stripped_strings)
                for hh in sp1.select("div.reindex-openingtimes table tr")
            ]
            raw_address = " ".join(
                sp1.select_one("div#reindex-detail-adress").stripped_strings
            )
            coord = sp1.select_one('meta[name="geo.position"]')["content"].split(";")
            if coord == [0, 0]:
                coord = ["", ""]
            phone = ""
            _pp = sp1.find("td", string=re.compile(r"Telefon:"))
            if _pp:
                phone = _pp.find_next_sibling().text.split("od.")[0].strip()
            yield SgRecord(
                page_url=page_url,
                location_name=sp1.select_one('span[itemprop="name"]').text.strip(),
                street_address=sp1.select_one(
                    'span[itemprop="street-address"]'
                ).text.strip(),
                city=sp1.select_one('span[itemprop="locality"]').text.strip(),
                zip_postal=sp1.select_one('span[itemprop="postal-code"]').text.strip(),
                country_code="Germany",
                phone=phone,
                latitude=coord[0],
                longitude=coord[1],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

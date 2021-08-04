from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import math
from concurrent.futures import ThreadPoolExecutor
from sglogging import SgLogSetup
import re

logger = SgLogSetup().get_logger("massageaddict")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = "https://www.massageaddict.ca/locations/"
locator_domain = "https://www.massageaddict.ca"
session = SgRequests().requests_retry_session()
max_workers = 8


def fetchConcurrentSingle(link):
    page_url = urljoin(locator_domain, link["href"])
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
            count = count + 1
            if count % reminder == 0:
                logger.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def request_with_retries(url):
    return session.get(url, headers=_headers)


def fetch_data():
    soup = bs(session.get(base_url, headers=_headers).text, "lxml")
    links = soup.select("div.mobileShow.mobileProv ul a")
    logger.info(f"{len(links)} found")
    for url, sp1 in fetchConcurrentList(links):
        locations = sp1.select("ul.clinicSearch li")
        for _ in locations:
            addr = list(_.select_one(".col-sm-8").stripped_strings)[-1].split(",")
            hours = []
            page_url = _.h2.a["href"]
            logger.info(page_url)
            sp2 = bs(request_with_retries(page_url).text, "lxml")
            try:
                coord = (
                    sp2.iframe["src"]
                    .split("!2d")[1]
                    .split("!3m")[0]
                    .split("!2m")[0]
                    .split("!3d")
                )
            except:
                try:
                    sp2.iframe["src"].split("&ll=")[1].split("&")[0].split(",")[::-1]
                except:
                    coord = ["", ""]
            _hr = sp2.find("", string=re.compile(r"^Hours"))
            if _hr:
                temp = list(_hr.find_parent("p").stripped_strings)
                for x, hh in enumerate(temp):
                    if hh == "Hours":
                        hours = temp[x + 1 :]
                        break
            else:
                _hr = sp2.find("", string=re.compile(r"^Mon "))
                if not _hr:
                    _hr = sp2.find("", string=re.compile(r"Mon-"))
                if _hr:
                    temp = list(_hr.find_parent("p").stripped_strings)
                    for x, hh in enumerate(temp):
                        if hh.startswith("Mon"):
                            hours = temp[x:]
                            break

            yield SgRecord(
                page_url=page_url,
                location_name=_.h2.text.strip(),
                street_address=" ".join(addr[:-3]),
                city=addr[-3].strip(),
                state=addr[-2].strip(),
                zip_postal=addr[-1].strip(),
                country_code="CA",
                phone=_.select_one("div.clinicSearchPhone").text.strip(),
                locator_domain=locator_domain,
                latitude=coord[1],
                longitude=coord[0],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

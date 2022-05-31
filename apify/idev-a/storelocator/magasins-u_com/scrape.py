from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.magasins-u.com"
base_url = "https://www.magasins-u.com/csd/Satellite?childpagename=portailu%2FUtilities%2FMagasin%2FGetMagasinsAvecFiltres&pagename=portailu%2FWrapper%2FAuthentication"


max_workers = 1


def fetchConcurrentSingle(_):
    page_url = locator_domain + _["urlMagasin"]
    logger.info(page_url)
    response = request_with_retries(page_url)
    return _, page_url, bs(response.text, "lxml")


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
    with SgRequests(proxy_country="us") as session:
        return session.get(url, headers=_headers)


def fetch_data():
    with SgRequests(proxy_country="us") as session:
        locations = session.get(base_url, headers=_headers).json()["data"]
        for _, page_url, sp1 in fetchConcurrentList(locations):
            phone = ""
            if sp1.select_one('span[itemprop="telephone"]'):
                phone = sp1.select_one('span[itemprop="telephone"]').text.strip()
            hours = []
            days = sp1.select("dl dt")
            times = sp1.select("dl dd")
            for x in range(len(days)):
                hours.append(f"{days[x].text.strip()} {times[x].text.strip()}")
            yield SgRecord(
                page_url=page_url,
                store_number=_["idMagasin"],
                location_name=_["libelleMagasin"],
                street_address=_["adresse"]
                .replace("\n", " ")
                .replace("\t", "")
                .replace("\r", ""),
                city=_["ville"],
                zip_postal=_["codePostal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="FR",
                location_type=page_url.split("/")[-1].split("-")[0],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

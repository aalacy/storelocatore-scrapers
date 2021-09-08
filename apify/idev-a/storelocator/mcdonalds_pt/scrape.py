from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import dirtyjson as json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import math
from concurrent.futures import ThreadPoolExecutor

logger = SgLogSetup().get_logger("mcdonalds")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mcdonalds.pt"
base_url = "https://www.mcdonalds.pt/restaurantes?t=&d="
max_workers = 16
session = SgRequests().requests_retry_session()


def fetchConcurrentSingle(link):
    page_url = locator_domain + link["Url"]
    response = request_with_retries(page_url)
    return page_url, link, bs(response.text, "lxml")


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
    return session.get(url, headers=_headers)


def _la(val):
    return (
        val.replace("&#39;", "'")
        .replace("&#170;", "å")
        .replace("&#231;", "ç")
        .replace("&#227;", "ã")
        .replace("&#233;", "é")
        .replace("&#201;", "É")
        .replace("&#186;", "°")
        .replace("&#225;", "á")
        .replace("&#243;", "ó")
        .replace("&#234;", "ê")
        .replace("&#193;", "Á")
        .replace("&#226;", "â")
        .replace("&#250;", "ú")
        .replace("&#245;", "õ")
        .replace("&#237;", "í")
        .replace("&#160;", "")
        .replace("&#195;", "Ã")
        .replace("&#199;", "Ç")
        .replace("&#218;", "Ú")
        .replace("&#211;", "Ó")
    )


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var restaurantsJson =")[1]
            .split("</script>")[0]
            .strip()[1:-1]
        )
        for page_url, _, sp1 in fetchConcurrentList(locations):
            logger.info(page_url)
            hours = []
            for hh in sp1.select("div.restaurantSchedule__service")[0].select("ul li"):
                if "Véspera Feriado" in hh.text:
                    continue
                hours.append(": ".join(hh.stripped_strings))
            ss = json.loads(sp1.find("script", type="application/ld+json").string)
            addr = ss["address"]
            yield SgRecord(
                page_url=page_url,
                location_name=_la(ss["name"]),
                street_address=_la(addr["streetAddress"]),
                city=_la(addr["addressLocality"]),
                state=_la(addr["addressRegion"]),
                zip_postal=_la(addr["postalCode"]),
                latitude=_["Lat"],
                longitude=_["Lng"],
                country_code="Portugal",
                phone=ss.get("telephone"),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

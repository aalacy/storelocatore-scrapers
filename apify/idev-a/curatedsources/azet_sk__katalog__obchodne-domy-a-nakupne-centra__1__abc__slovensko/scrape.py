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

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


base_url = (
    "https://www.azet.sk/katalog/obchodne-domy-a-nakupne-centra/{}/abc/slovensko/"
)
locator_domain = (
    "https://azet.sk/katalog/obchodne-domy-a-nakupne-centra/1/abc/slovensko"
)

max_workers = 8


def fetchConcurrentSingle(link):
    page_url = urljoin("", link.h2.a["href"])
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
    with SgRequests() as session:
        return session.get(url, headers=_headers)


def _p(val):
    if (
        val
        and val.replace("(", "")
        .replace(")", "")
        .replace("+", "")
        .replace("-", "")
        .replace(".", " ")
        .replace("to", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    ):
        return val
    else:
        return ""


def fetch_data():
    with SgRequests() as session:
        page = 1
        while True:
            soup = bs(session.get(base_url.format(page), headers=_headers).text, "lxml")
            links = soup.select("div.record")
            if not links:
                break
            page += 1
            logger.info(f"{len(links)} found")
            for page_url, link, sp1 in fetchConcurrentList(links):
                logger.info(page_url)
                addr = list(
                    sp1.select_one("div.address div.mainContact").stripped_strings
                )[1:]
                hours = []
                for hh in sp1.select("section#otvaracie-hodiny-firmy div.span25"):
                    if hh.strong or "Poznámka" in hh.text:
                        break
                    hours.append(" ".join(hh.stripped_strings))
                coord = (
                    sp1.select_one("iframe#mainMap")["src"]
                    .split("q=loc:")[1]
                    .split("&")[0]
                    .split(",")
                )
                location_name = link.h2.text.strip()
                location_type = "Department store"
                if "centrum" in link.select_one("div.description").text:
                    location_type = "Shopping center"
                if (
                    "centrum" in location_name.lower()
                    or "shopping" in location_name.lower()
                ):
                    location_type = "Shopping center"

                try:
                    phone = _p(sp1.select("div.mainContact")[1].text.strip())
                except:
                    phone = ""
                yield SgRecord(
                    page_url=page_url,
                    location_name=location_name,
                    street_address=sp1.select_one(
                        'span[itemprop="streetAddress"]'
                    ).text.strip(),
                    city=sp1.select_one(
                        'span[itemprop="addressLocality"]'
                    ).text.strip(),
                    zip_postal=sp1.select_one(
                        'span[itemprop="postalCode"]'
                    ).text.strip(),
                    country_code="Slovakia",
                    phone=phone,
                    locator_domain=locator_domain,
                    latitude=coord[0],
                    longitude=coord[1],
                    location_type=location_type,
                    hours_of_operation="; ".join(hours)
                    .replace("\n", "")
                    .replace("\r", " ")
                    .replace("●", " "),
                    raw_address=" ".join(addr),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

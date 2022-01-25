from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("wellsfargo")

locator_domain = "https://www.wellsfargo.com/"
base_url = "https://www.wellsfargo.com/locator/"
payload_url = "https://www.wellsfargo.com/locator/as/getpayload"
sitemap1 = "https://www.wellsfargo.com/locator/sitemap1"
sitemap2 = "https://www.wellsfargo.com/locator/sitemap2"

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.wellsfargo.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

session = SgRequests()


def parallel_run_one(link):
    logger.info(f"[1] {link}")
    session.get(link, headers=_headers)
    locations = session.post(payload_url, headers=_headers).json()["searchResults"]

    for _ in locations:
        hours_of_operation = "; ".join(_.get("arrDailyEvents", []))
        if (
            _.get("incidentMessage", {}).get("incidentDesc", "").lower()
            == "temporary closure"
        ):
            hours_of_operation = "Temporary closed"

        if _.get("incidentMessage", {}).get("outletStatusDesc", "").lower() == "closed":
            hours_of_operation = "closed"

        if "ATM" in _["locationType"]:
            hours_of_operation = _["serviceDetails"]["atmServices"]["atmSiteHours"]

        if "Hours vary" in hours_of_operation:
            hours_of_operation = ""

        yield SgRecord(
            location_name=_["branchName"],
            street_address=_["locationLine1Address"],
            city=_["city"],
            state=_["state"],
            zip_postal=_["postalcode"],
            country_code="US",
            phone=_["phone"],
            latitude=_["latitude"],
            longitude=_["longitude"],
            location_type=_["locationType"],
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )


def scrape_loc_urls(location_urls):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(parallel_run_one, link) for link in location_urls]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception:
                pass


def scrape_loc_urls_two(location_urls):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(parallel_run_two, link) for link in location_urls]
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception:
                pass


def parallel_run_two(link):
    logger.info(f"[2] {link}")
    res = session.get(link, headers=_headers)
    if (
        "error.html" in str(res.url)
        or "PageNotFound.html" in str(res.url)
        or "The transaction failed" in res.text
    ):
        return None
    sp1 = bs(res.text, "lxml")
    if sp1.find("", string=re.compile(r"could not find")):
        return None
    location_type = sp1.select_one("div.fn.heading").text.strip()
    try:
        coord = (
            sp1.select_one("div.mapView img")["src"]
            .split("Road/")[1]
            .split("/")[0]
            .split(",")
        )
    except:
        coord = ["", ""]
    hours = []
    _hr = sp1.find("h2", string=re.compile(r"Lobby Hours", re.IGNORECASE))
    if not _hr:
        _hr = sp1.find("h3", string=re.compile(r"^ATMs", re.IGNORECASE))
    if _hr:
        hours = list(_hr.find_next_sibling().stripped_strings)

    if not hours:
        if sp1.select("div.incidentMessage p"):
            hours = [sp1.select("div.incidentMessage p")[-1].text.strip()]
        elif sp1.select("div.location-timings p"):
            hours = [sp1.select("div.location-timings p")[1].text.strip()]
            if "Hours vary" in hours[0]:
                hours = []

    addr = [aa for aa in list(sp1.address.stripped_strings) if aa.strip() != ","]
    street_address = " ".join(addr[1].split(",")[:-1])
    phone = ""
    if sp1.find("a", href=re.compile(r"tel:")):
        phone = sp1.find("a", href=re.compile(r"tel:")).text.strip()
    yield SgRecord(
        page_url=link,
        location_name=addr[0],
        street_address=street_address,
        city=addr[1].split(",")[-1],
        state=addr[2],
        zip_postal=addr[3],
        country_code="US",
        phone=phone,
        latitude=coord[0],
        longitude=coord[1],
        location_type=location_type,
        locator_domain=locator_domain,
        hours_of_operation=" ".join(hours),
    )


def fetch_data():

    # sitemap2
    links = (
        bs(session.get(sitemap2, headers=_headers).text, "lxml")
        .text.strip()
        .split("\n")
    )
    logger.info(f"{len(links)} sitemap2")
    results = scrape_loc_urls_two(links)

    for result in results:
        for item in result:
            yield item

    # sitemap1
    links = bs(session.get(sitemap1).text, "lxml").text.strip().split("\n")
    logger.info(f"{len(links)} sitemap1")
    results = scrape_loc_urls(links)

    for result in results:
        for item in result:
            yield item


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            ),
            duplicate_streak_failure_factor=150,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

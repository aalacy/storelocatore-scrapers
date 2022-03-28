from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sgrequests.sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.oeffnungszeitenbuch.de"
base_url = "https://www.oeffnungszeitenbuch.de/einkaufszentrum-uebersicht.html"


def record_initial_requests(http, state):
    logger.info(f"IP: {http.my_public_ip()}")
    soup = bs(http.get(base_url, headers=_headers).text, "lxml")
    cities = soup.find("div", {"id": "textbereich"})
    cities = cities.find("table").find_all("a")
    for city in cities:  # Sliced for testing
        city_base = city["href"]
        logger.info(city_base)
        logger.info(f"IP: {http.my_public_ip()}")
        pages = bs(
            SgRequests.raise_on_err(http.get(city_base, headers=_headers)).text, "lxml"
        )
        pages = pages.find("div", {"id": "textbereich"})
        pages = pages.find("table")
        all_links = pages.find_all("a", {"href": True})
        for link in all_links:
            page_url = link["href"]
            state.push_request(
                SerializableRequest(url=page_url, context={"link": link.text.strip()})
            )
    return True


def page(http, next_r):
    page = None
    try:
        logger.info(f"IP: {http.my_public_ip()}")
        page = SgRequests.raise_on_err(http.get(next_r.url))
        return page
    except Exception as e:
        if "404" in str(e):
            return None
        else:
            raise (f"{str(e)}")


def producer(http, state):
    for next_r in state.request_stack_iter():
        yield {
            "page_url": next_r.url,
            "link": next_r.context.get("link") if next_r.context else None,
            "text": page(http, next_r),
        }


def consumer(resp_generator, writer):
    for response in resp_generator:
        if response["text"]:
            sp2 = bs(response["text"].text, "lxml")
            addr = [
                i
                for i in sp2.find("div", {"id": "textbereich"})
                .find("table")
                .find("td")
                .stripped_strings
            ]
            rawa = [addr[8], addr[9], addr[10]]
            rawa = " ".join(rawa)
            parsed = parse_address_intl(rawa + ", Germany")
            street_address = ""
            city = parsed.city
            zip_postal = parsed.postcode
            if zip_postal:
                street_address = rawa.split(zip_postal)[0].strip()
            location_name = response["link"] if response["link"] else addr[0]
            writer.write_row(
                SgRecord(
                    page_url=response["page_url"],
                    location_name=location_name.split(":")[-1],
                    street_address=street_address,
                    city=city,
                    zip_postal=zip_postal,
                    country_code="DE",
                    phone=SgRecord.MISSING,
                    locator_domain=locator_domain,
                    hours_of_operation=SgRecord.MISSING,
                    raw_address=rawa,
                )
            )


def fetch_data(http, state, writer):
    consumer(producer(http, state), writer)


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests(proxy_country="DE") as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            fetch_data(http, state, writer)

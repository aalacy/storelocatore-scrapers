from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sgrequests.sgrequests import SgRequests, SgRequestsAsync
import asyncio
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.oeffnungszeitenbuch.de"
base_url = "https://www.oeffnungszeitenbuch.de/einkaufszentrum-uebersicht.html"


def record_initial_requests(http, state):
    soup = bs(http.get(base_url, headers=_headers).text, "lxml")
    cities = soup.select("#textbereich > div > table:nth-child(4)")
    for city in cities:  # Sliced for testing
        city_base = city.a["href"]
        logger.info(city_base)
        pages = bs(
            SgRequests.raise_on_err(http.get(city_base, headers=_headers)).text, "lxml"
        ).select("#textbereich > div > table:nth-child(2)")
        all_links = []
        for page in pages:
            all_links = all_links + page.find_all("a")
        for link in all_links:
            page_url = link["href"]
            state.push_request(
                SerializableRequest(url=page_url, context={"link": link.text.strip()})
            )
    return True


async def producer(state):
    async with SgRequestsAsync() as httpx:
        for next_r in state.request_stack_iter():
            yield {
                "page_url": next_r.url,
                "link": next_r.context.get("link") if next_r.context else None,
                "text": await SgRequests.raise_on_err(httpx.get(next_r.url)),
            }


async def consumer(resp_generator, writer):
    async for response in resp_generator:
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
        parsed = parse_address_intl(rawa)
        realadd = parsed.street_address_1 if parsed.street_address_1 else ""
        realadd = realadd + parsed.street_address_2 if parsed.street_address_2 else ""
        writer.write_row(
            SgRecord(
                page_url=response["page_url"],
                location_name=response["link"] if response["link"] else addr[0],
                street_address=realadd if realadd else SgRecord.MISSING,
                city=parsed.city if parsed.city else SgRecord.MISSING,
                zip_postal=parsed.postcode if parsed.postcode else SgRecord.MISSING,
                country_code="DE",
                phone=SgRecord.MISSING,
                locator_domain=locator_domain,
                hours_of_operation=SgRecord.MISSING,
                raw_address=rawa,
            )
        )


def fetch_data(state, writer):
    asyncio.get_event_loop().run_until_complete(consumer(producer(state), writer))


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            fetch_data(state, writer)

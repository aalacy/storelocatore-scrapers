from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sgrequests.sgrequests import SgRequests, SgRequestsAsync
import asyncio

logger = SgLogSetup().get_logger("")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.oeffnungszeitenbuch.de"
base_url = "https://www.oeffnungszeitenbuch.de/"


def record_initial_requests(http, state):
    soup = bs(http.get(base_url, headers=_headers).text, "lxml")
    cities = soup.select("div#textbereich > table a")
    for city in cities[-5:-4]:  # Sliced for testing
        city_base = city["href"]
        logger.info(city_base)
        pages = bs(http.get(city_base, headers=_headers).text, "lxml").select(
            "select#seitennr option"
        )
        for page in pages[:1]:  # Sliced for testing
            section_url = city_base.split("-")[0] + "-" + page.text + ".html"
            logger.info(section_url)
            links = bs(http.get(section_url, headers=_headers).text, "lxml").select(
                "div.cboxserp"
            )
            for link in links:
                page_url = link.a["href"]
                state.push_request(
                    SerializableRequest(
                        url=page_url, context={"link": link.a.text.strip()}
                    )
                )
    return True


async def producer(state):
    async with SgRequestsAsync() as httpx:
        for next_r in state.request_stack_iter():
            yield {
                "page_url": next_r.url,
                "link": next_r.context.get("link") if next_r.context else "<MISSING>",
                "text": await httpx.get(next_r.url),
            }


async def consumer(resp_generator, writer):
    async for response in resp_generator:
        sp2 = bs(response["text"].text, "lxml")
        addr = list(sp2.select("span.entryAdrFnt > div")[1].stripped_strings)[:3]
        phone = ""
        if sp2.select_one("span.telClk"):
            phone = sp2.select_one("span.telClk").text.strip()
        hours = []
        for hh in sp2.select("table.zeitenTbl tr"):
            td = hh.select("td")
            if len(td) == 1:
                break
            hours.append(" ".join(hh.stripped_strings))
        writer.write_row(
            SgRecord(
                page_url=response["page_url"],
                location_name=response["link"],
                street_address=addr[0],
                city=addr[-1],
                zip_postal=addr[1],
                country_code="DE",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(addr),
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

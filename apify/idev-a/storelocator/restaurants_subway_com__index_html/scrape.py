from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from urllib.parse import urljoin
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("subway")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

base_url = "https://restaurants.subway.com/index.html"
locator_domain = "https://restaurants.subway.com/"


def fetchConcurrentList(links, http):
    output = []
    for link in links:
        page_url = urljoin(locator_domain, link["href"].replace("../", ""))
        if "additional-locations" not in page_url:
            output.append(
                (page_url, bs(http.get(page_url, headers=_headers).text, "lxml"))
            )
    return output


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        res = http.get(next_r.url, headers=_headers)
        if res.status_code != 200:
            continue
        sp1 = bs(res.text, "lxml")
        street_address = ""
        if sp1.select_one(".c-address-street-1"):
            street_address = sp1.select_one(".c-address-street-1").text.strip()
        if sp1.select_one(".c-address-street-2"):
            street_address += " " + sp1.select_one(".c-address-street-2").text.strip()
        zip_postal = state = city = phone = ""
        if sp1.select_one(".c-address-city"):
            city = sp1.select_one(".c-address-city").text.strip()
        if sp1.select_one(".c-address-postal-code"):
            zip_postal = sp1.select_one(".c-address-postal-code").text.strip()
        if sp1.select_one(".c-address-state"):
            state = sp1.select_one(".c-address-state").text.strip()
        if sp1.select_one("div.Core-col div#phone-main"):
            phone = sp1.select_one("div.Core-col div#phone-main").text.strip()
        hours = []
        if sp1.select("table.c-hours-details"):
            for hh in sp1.select("table.c-hours-details")[0].select("tbody tr"):
                hours.append(hh["content"])

        yield SgRecord(
            page_url=next_r.url,
            location_name=list(sp1.select_one('h1[itemprop="name"]').stripped_strings)[
                -1
            ],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=sp1.select_one(".c-address-country-name").text.strip(),
            phone=phone,
            locator_domain=locator_domain,
            latitude=sp1.select_one('meta[itemprop="latitude"]')["content"],
            longitude=sp1.select_one('meta[itemprop="longitude"]')["content"],
            hours_of_operation="; ".join(hours).replace("–", "-"),
        )


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    countries = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "ul.Directory-listLinks a"
    )
    logger.info(f"{len(countries)} found")
    for country_url, sp1 in fetchConcurrentList(countries, http):
        states = sp1.select("ul.Directory-listLinks a")
        for state_url, sp2 in fetchConcurrentList(states, http):
            cities = sp2.select("ul.Directory-listLinks a")
            if cities:
                for city_url, sp3 in fetchConcurrentList(cities, http):
                    loc1s = sp3.select("ul.Directory-listTeasers a")
                    if loc1s:
                        for page_url1, sp5 in fetchConcurrentList(loc1s, http):
                            state.push_request(SerializableRequest(url=page_url1))
                    else:
                        state.push_request(SerializableRequest(url=city_url))
            else:
                locs = sp2.select("ul.Directory-listTeasers a")
                if locs:
                    for page_url, sp4 in fetchConcurrentList(locs, http):
                        state.push_request(SerializableRequest(url=page_url))
                else:
                    state.push_request(SerializableRequest(url=state_url))

    return True


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.CITY,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)

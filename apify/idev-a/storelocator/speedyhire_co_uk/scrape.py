from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("speedyservices")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.speedyservices.com"
base_url = "https://www.speedyservices.com/depot/a-z"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    areas = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "div.result-depot a"
    )
    for area in areas:
        area_url = locator_domain + area["href"]
        state.push_request(SerializableRequest(url=area_url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        res = http.get(next_r.url, headers=_headers).text
        _ = bs(res, "lxml")
        raw_address = (
            _.select_one("div#Address p")
            .text.replace("\n", "")
            .replace("\r", " ")
            .strip()
        )
        addr = raw_address.split(",")
        street_address = []
        for aa in addr[:-4]:
            if "@" in aa:
                continue
            street_address.append(aa)
        hours = []
        temp = list(_.select_one("div#working-hours").stripped_strings)
        for x in range(0, len(temp), 2):
            hours.append(f"{temp[x]} {temp[x+1]}")
        coord = res.split("new google.maps.LatLng(")[1].split(")")[0].split(",")
        yield SgRecord(
            page_url=next_r.url,
            location_name=_.select_one("div#Address h1").text.strip(),
            street_address=" ".join(street_address).strip(),
            city=addr[-4].strip(),
            state=addr[-3].strip(),
            zip_postal=addr[-1].strip(),
            country_code="UK",
            phone=_.select_one("div#Address a").text.strip(),
            latitude=coord[0],
            longitude=coord[1],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
            raw_address=raw_address,
        )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)

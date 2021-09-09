from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("blueinc")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.blueinc.co.uk"
base_url = "https://www.blueinc.co.uk/map"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "a.store-locator__store__link.button"
    )
    for loc in locs:
        url = locator_domain + loc["href"]
        state.push_request(SerializableRequest(url=url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        res = http.get(next_r.url, headers=_headers).text
        coord = res.split("new google.maps.LatLng(")[1].split(")")[0].split(",")
        sp1 = bs(res, "lxml")
        raw_address = list(
            sp1.select_one("div.store-locator__store__col p").stripped_strings
        )
        addr = parse_address_intl(", ".join(raw_address) + ", UK")
        street_address = addr.street_address_1 or ""
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        if not city:
            city = raw_address[-2].replace("Buttercrane Quay", "").strip()
        if not street_address:
            street_address = raw_address[0]
        if city:
            if raw_address[1] != city:
                street_address += " " + raw_address[1]
            if street_address.startswith(city):
                street_address = ""
        phone = ""
        if sp1.select_one("div.store-locator__store__col a"):
            phone = sp1.select_one("div.store-locator__store__col a").text.strip()
        yield SgRecord(
            page_url=next_r.url,
            location_name=sp1.select_one(
                "div.store-locator__store__col h1"
            ).text.strip(),
            street_address=street_address,
            city=city,
            state=addr.state,
            zip_postal=raw_address[-1],
            country_code="uk",
            latitude=coord[0],
            longitude=coord[1],
            phone=phone,
            locator_domain=locator_domain,
            raw_address=" ".join(raw_address),
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

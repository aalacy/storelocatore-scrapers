from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup
import json
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("suitdirect")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.suitdirect.co.uk/"
base_url = "https://www.suitdirect.co.uk/store-locator/"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = json.loads(
        http.get(base_url, headers=_headers)
        .text.split("<script type=application/ld+json>")[1]
        .split("</script>")[0]
    )
    for loc in locs:
        if not loc.get("@id"):
            continue
        url = locator_domain + loc["@id"]
        state.push_request(SerializableRequest(url=url, context={"loc": loc}))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        _ = next_r.context.get("loc")
        sp1 = bs(http.get(next_r.url, headers=_headers).text, "lxml")
        raw_address = list(
            sp1.select_one("div.store-information__address").stripped_strings
        )[1:-1]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hours = []
        if _["openingHours"]:
            hours = [
                hh.text.strip() for hh in bs(_["openingHours"], "lxml").select("ul li")
            ]
        yield SgRecord(
            page_url=next_r.url,
            location_name=_["name"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=_["address"][0]["postalCode"],
            country_code="UK",
            latitude=sp1.select_one("div#storeMap")["data-lat"],
            longitude=sp1.select_one("div#storeMap")["data-lng"],
            phone=_["telephone"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
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

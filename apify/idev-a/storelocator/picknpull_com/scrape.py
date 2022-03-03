from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("picknpull")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.picknpull.com"
base_url = "https://www.picknpull.com/api/locations/schnlocations"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = http.get(base_url, headers=_headers).json()
    for loc in locs:
        url = f"https://www.picknpull.com/locations/{loc['locationID']}/{loc['mapTextLine1'].lower().replace(' ', '-').replace(',','').replace('(','').replace(')','')}"
        state.push_request(SerializableRequest(url=url, context=({"loc": loc})))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        loc = next_r.context.get("loc")
        url = f"https://www.picknpull.com/api/locations/{loc['locationID']}?language=english"
        _ = http.get(url, headers=_headers).json()
        street_address = _["address1"]
        if _["address2"]:
            street_address += " " + _["address2"]
        hours = [
            hh["content"]
            for hh in bs(_["hours"], "lxml").select('span[itemprop="openingHours"]')
        ]
        if not hours:
            for hh in list(bs(_["hours"], "lxml").stripped_strings):
                if "Note" in hh or "/" in hh:
                    break
                hours.append(hh)
        yield SgRecord(
            page_url=next_r.url,
            store_number=_["locationID"],
            location_name=_["name"],
            street_address=street_address,
            city=_["city"],
            state=_["state"],
            zip_postal=_["postalCode"],
            country_code=_["country"],
            phone=_["publicPhone1"],
            latitude=_["mapLatitude"],
            longitude=_["mapLongitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours).replace("•", "").strip(),
        )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)

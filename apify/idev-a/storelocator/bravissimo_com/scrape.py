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

logger = SgLogSetup().get_logger("bravissimo")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.bravissimo.com"
base_url = "https://www.bravissimo.com/shops/all/"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "div.c-shops-section a.u-block-link"
    )
    for loc in locs:
        url = locator_domain + loc["href"]
        state.push_request(SerializableRequest(url=url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        sp1 = bs(http.get(next_r.url, headers=_headers).text, "lxml")
        _ = json.loads(sp1.find("script", type="application/ld+json").string)
        addr = _["address"]
        zip_postal = state = ""
        if addr["addressCountry"] == "USA":
            zip_postal = addr["postalCode"].split()[-1]
            state = addr["postalCode"].split()[0]
        else:
            zip_postal = addr["postalCode"]
            state = addr["addressRegion"]
        yield SgRecord(
            page_url=next_r.url,
            location_name=sp1.select_one("h1.c-bandeau__title").text.strip(),
            street_address=addr["streetAddress"],
            city=addr["addressLocality"],
            state=state,
            zip_postal=zip_postal,
            country_code=addr["addressCountry"],
            latitude=_["geo"]["latitude"],
            longitude=_["geo"]["longitude"],
            phone=_.get("telephone"),
            locator_domain=locator_domain,
            hours_of_operation=_.get("openingHours"),
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

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

logger = SgLogSetup().get_logger("bodynbrain")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.bodynbrain.com"
base_url = "https://www.bodynbrain.com/locations"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    areas = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "ul.centerList li.link a"
    )
    for area in areas:
        url = locator_domain + area["href"]
        state.push_request(SerializableRequest(url=url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)

        sp1 = bs(http.get(next_r.url, headers=_headers).text, "lxml")
        _ = json.loads(sp1.find("script", type="application/ld+json").string)
        addr = _["address"]
        street_address = (
            addr["streetAddress"].split(addr["addressLocality"].strip())[0].strip()
        )
        if street_address.isdigit():
            street_address = addr["streetAddress"].strip()
        hours = []
        days = [
            dd.text.strip().split()[0] for dd in sp1.select("aside.sidebar h5.date")
        ]
        times = [
            dd.select("p")[-1].text.strip()
            for dd in sp1.select("aside.sidebar div.DateClass div.eventClass")
        ]
        for x in range(len(days)):
            hours.append(f"{days[x]}: {times[x]}")
        yield SgRecord(
            page_url=next_r.url,
            location_name=_["name"],
            street_address=street_address,
            city=addr["addressLocality"].strip(),
            state=addr["addressRegion"].strip(),
            zip_postal=addr["postalCode"].strip(),
            country_code="US",
            phone=_["telephone"],
            latitude=_["geo"]["latitude"],
            longitude=_["geo"]["longitude"],
            locator_domain=locator_domain,
            hours_of_operation="; ".join(hours),
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

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("pizzahut")

_headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,ko;q=0.8",
    "content-type": "application/json",
    "lang": "en",
    "origin": "https://kuwait.pizzahut.me",
    "referer": "https://kuwait.pizzahut.me/",
    "client": "eb0b3aa0-4ab7-4c9b-8ef0-bc54bea84ca5",
    "if-none-match": 'W/"c67-RfvFOzR4Li2deW0/nRL5kFgbo0I"',
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://kuwait.pizzahut.me"
base_url = "https://apimes1.phdvasia.com/v2/product-hut-fe/localization/getListArea"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    areas = http.get(base_url, headers=_headers).json()["data"]["items"]
    for area in areas:
        area_url = f"https://apimes1.phdvasia.com/v2/product-hut-fe/localization/getBlockByArea?area={area['area'].replace(' ','%20')}"
        logger.info(area_url)
        state.push_request(SerializableRequest(url=area_url))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        locations = http.get(next_r.url, headers=_headers).json()["data"]["item"][
            "block"
        ]
        for _ in locations:
            yield SgRecord(
                store_number=_["id"],
                location_name=_["name"],
                street_address=_["name"],
                city=_["customize"]["CityName"],
                state=_["customize"]["ProvinceName"],
                country_code="Kuwait",
                locator_domain=locator_domain,
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

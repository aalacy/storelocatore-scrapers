from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("31ice")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.31ice.co.jp/"
base_url = "https://store.31ice.co.jp/31ice/"
loc_url = "https://store.31ice.co.jp/31ice/api/proxy2/shop/list?datum=wgs84&limit=500&add=detail&business-hours=all&offset={}"


def _cs(_states, addr):
    city = ""
    _state = ""
    street_address = ""
    is_found = False
    for ss, cities in _states.items():
        if is_found:
            break
        for cc in cities:
            if cc in addr:
                _state = ss
                city = cc
                street_address = addr.split(cc)[-1]
                is_found = True
                break

    return street_address, city, _state


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    _states = {}
    for ss in bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "ul#w_7_areamap_1_1-region > li"
    ):
        cities = []
        for cc in ss.select("ul li"):
            cities.append(list(cc.stripped_strings)[0])
        _states[list(ss.dt.stripped_strings)[0]] = cities
    offset = 0
    while True:
        res = http.get(loc_url.format(offset), headers=_headers).json()
        locations = res["items"]
        if not locations:
            break
        logger.info(f"[{offset}] {len(locations)}")
        offset += len(locations)
        for _ in locations:
            page_url = "https://store.31ice.co.jp/31ice/spot/detail?code={}".format(
                _["code"]
            )
            state.push_request(
                SerializableRequest(url=page_url, context={"_": _, "_states": _states})
            )

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        _ = next_r.context.get("_")
        tr = bs(http.get(next_r.url, headers=_headers).text, "lxml").select(
            "div#main-container table tr"
        )
        _aa = [aa.strip() for aa in tr[0].td.text.strip().split("\n")]
        raw_address = _aa[1]
        street_address, city, _state = _cs(next_r.context.get("_states"), raw_address)
        hours_of_operation = ""
        if len(tr) > 2:
            hours_of_operation = tr[2].td.text.strip()
        yield SgRecord(
            page_url=next_r.url,
            store_number=_["code"],
            location_name=_["name"],
            street_address=street_address,
            city=city,
            state=_state,
            zip_postal=_["postal_code"],
            country_code="JP",
            phone=_["phone"],
            latitude=_["coord"]["lat"],
            longitude=_["coord"]["lon"],
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init",
                default_factory=lambda: record_initial_requests(http, state),
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)

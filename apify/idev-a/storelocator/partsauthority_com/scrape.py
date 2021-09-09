from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl
import re
import bs4

logger = SgLogSetup().get_logger("partsauthority")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://partsauthority.com"
base_url = "https://partsauthority.com/locations/"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = (
        bs(http.get(base_url, headers=_headers).text, "lxml")
        .find("", string=re.compile(r"^Locations$"))
        .find_parent("a")
        .find_next_sibling("ul")
        .select("a")[1:]
    )
    logger.info(f"{len(locs)} locs found")
    for loc in locs:
        page_url = loc["href"]
        state.push_request(SerializableRequest(url=page_url))

    return True


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        locations = bs(http.get(next_r.url, headers=_headers).text, "lxml").select(
            'div[data-elementor-type="single"] div.elementor-col-25 div.elementor-text-editor'
        )
        logger.info(f"[{len(locations)}] {next_r.url}")
        for _ in locations:
            if not _.h3:
                continue
            raw_address = list(_.p.stripped_strings)
            store_number = raw_address[0].split("–")[-1]
            del raw_address[0]
            hours = []
            _hr = _.select_one("span strong").find_parent("p")
            hours = []
            for tt in _hr.find_next_siblings("p"):
                temp = []
                _tt = list(tt.children)
                for x, hh in enumerate(_tt):
                    _hh = ""
                    if type(hh) == bs4.element.NavigableString:
                        _hh = hh
                    else:
                        _hh = hh.text
                    if "Online" in _hh or "Website" in _hh:
                        break
                    if hh.name != "br":
                        temp.append(_hh)
                    if temp and (hh.name == "br" or x == len(_tt) - 1):
                        hours.append(" ".join(temp))
                        temp = []
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                page_url=next_r.url,
                store_number=store_number,
                location_name=_.h3.text.strip(),
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="US",
                phone=_hr.text.strip(),
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(raw_address),
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

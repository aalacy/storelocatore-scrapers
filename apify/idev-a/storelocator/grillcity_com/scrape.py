from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from typing import Iterable
from sgscrape.pause_resume import SerializableRequest, CrawlState, CrawlStateSingleton
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl


logger = SgLogSetup().get_logger("grillcity")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.grillcity.com"
base_url = "https://www.grillcity.com/"


def record_initial_requests(http: SgRequests, state: CrawlState) -> bool:
    locs = bs(http.get(base_url, headers=_headers).text, "lxml").select(
        "ul.sf-menu > li"
    )
    for loc in locs:
        if "page_item_has_children" in loc["class"]:
            for ll in loc.select("ul > li > ul a"):
                state.push_request(SerializableRequest(url=ll["href"]))
        else:
            state.push_request(SerializableRequest(url=loc.a["href"]))

    return True


def fetch_records(http: SgRequests, state: CrawlState) -> Iterable[SgRecord]:
    for next_r in state.request_stack_iter():
        loc = bs(http.get(next_r.url, headers=_headers).text, "lxml")
        logger.info(next_r.url)
        temp = list(loc.select_one("div.footer-page-branch p").stripped_strings)
        locations = []
        location_name = loc.select_one("div.footer-page-branch h3").text.strip()
        if len(temp) > 1:
            for x in range(0, len(temp), 2):
                locations.append(f"{temp[x]} {temp[x+1]}")
        else:
            locations = temp
        for _ in locations:
            _ss = _.split("–")
            if len(_ss) > 1:
                location_name = _ss[0].strip()
            raw_address = _ss[-1].split("Tel")[0].strip()
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            country = "US"
            if "canada" in next_r.url:
                country = "CA"
            phone = ""
            if "Tel" in _:
                phone = _.split("Tel:")[-1].strip()
            yield SgRecord(
                page_url=next_r.url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=country,
                phone=phone,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.CITY, SgRecord.Headers.PHONE})
        )
    ) as writer:
        with SgRequests() as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)

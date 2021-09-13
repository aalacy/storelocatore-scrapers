from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("sknclinics")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://www.sknclinics.co.uk"
base_url = "https://www.sknclinics.co.uk/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMrQ0ilHSAQkVZ5QWeLoUA0WjY4ECyaXFJfm5bpmpOSkQsVqlWgAoVxcl"


def record_initial_requests(http, state):
    markders = http.get(base_url, headers=_headers).json()["markers"]
    for marker in markders:
        url = marker["link"]
        if not url.startswith("http"):
            url = locator_domain + url
        state.push_request(SerializableRequest(url=url, context={"marker": marker}))

    return True


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        _ = next_r.context.get("marker")
        if _["description"]:
            _addr = list(bs(_["description"], "lxml").stripped_strings)
        else:
            _addr = list(bs(_["address"], "lxml").stripped_strings)

        if len(_addr) == 1:
            _addr = _addr[0].split("\n")
        raw_address = ",".join(_addr)
        if not raw_address.lower().endswith("uk"):
            raw_address += ", UK"
        zip_postal = raw_address.split(",")[-2]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        if city and city.lower() in zip_postal.lower():
            city = ""
        state = addr.state
        phone = (
            bs(http.get(next_r.url, headers=_headers).text, "lxml")
            .select_one("a.map-times-001__link")
            .text.strip()
        )
        yield SgRecord(
            page_url=next_r.url,
            store_number=_["id"],
            location_name=_["title"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal.split("(")[0].replace("Tunbridge Wells", "").strip(),
            country_code="UK",
            phone=phone,
            latitude=_["lat"],
            longitude=_["lng"],
            locator_domain=locator_domain,
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

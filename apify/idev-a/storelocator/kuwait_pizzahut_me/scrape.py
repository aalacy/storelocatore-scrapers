from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl


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
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}
locator_domain = "https://kuwait.pizzahut.me"
base_url = "https://apimes1.phdvasia.com/v2/product-hut-fe/localization/getListArea"
client_url = "https://kuwait.pizzahut.me/js/1.1f6c418395905f478590.js"


def record_initial_requests(http, state):
    areas = http.get(base_url, headers=_headers).json()["data"]["items"]
    logger.info(f"{len(areas)} found")
    for area in areas:
        area_url = f"https://apimes1.phdvasia.com/v1/product-hut-fe/area/list_outlets?name={area['area'].replace(' ','%20')}&order_type=C"
        state.push_request(SerializableRequest(url=area_url))

    return True


def fetch_records(http, state):
    for next_r in state.request_stack_iter():
        logger.info(next_r.url)
        locations = []
        _headers["client"] = (
            http.get(client_url)
            .text.split("CLIENT_ID:")[1]
            .split("GOOGLE_API_KEY")[0]
            .strip()[1:-2]
        )
        res = http.get(next_r.url, headers=_headers)
        if res.status_code != 200:
            continue
        locations = res.json()["data"]["items"]
        for _ in locations:
            raw_address = _["address"]
            if "Kuwait" not in raw_address:
                raw_address += ", Kuwait"
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            yield SgRecord(
                store_number=_["id"],
                location_name=_["name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                phone=_["phone"].split("/")[0],
                latitude=_["lat"],
                longitude=_["long"],
                country_code="Kuwait",
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    state = CrawlStateSingleton.get_instance()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        with SgRequests(proxy_country="us") as http:
            state.get_misc_value(
                "init", default_factory=lambda: record_initial_requests(http, state)
            )
            for rec in fetch_records(http, state):
                writer.write_row(rec)

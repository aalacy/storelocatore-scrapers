import json
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgselenium import SgChrome
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.tarragona.cl"
base_url = "https://www.tarragona.cl/locales"
json_url = r"https://api.getjusto.com/graphql\?operationName\=getStoresZones"


def fetch_data():
    with SgChrome() as driver:
        driver.get(base_url)
        rr = driver.wait_for_request(json_url, timeout=20)
        locations = json.loads(rr.response.body)["data"]["stores"]["items"]
        for _ in locations:
            raw_address = (
                _["address"]["address"] + " " + _["address"]["addressSecondary"]
            )
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = []
            for hh in _["humanSchedule"]:
                hours.append(f"{hh['days']}: {hh['schedule']}")
            yield SgRecord(
                page_url=base_url,
                location_name=_["name"],
                street_address=_["address"]["address"],
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["address"]["location"]["lat"],
                longitude=_["address"]["location"]["lng"],
                country_code="Chile",
                phone=_["phone"],
                location_type=_["__typename"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("―", "-"),
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

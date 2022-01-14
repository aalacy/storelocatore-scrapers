from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import demjson as json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.cardzoneltd.com"
base_url = "https://www.cardzoneltd.com/find-a-store/"


def fetch_data():
    with SgRequests() as session:
        locations = json.decode(
            json.decode(
                session.get(base_url, headers=_headers)
                .text.split("var wcsl_js_lang =")[1]
                .split("</script>")[0]
                .strip()[:-1]
            )["wsl_store_details_json"].replace('\\\\"', "'")
        )
        for _ in locations:
            addr = parse_address_intl(_["wsl_street"] + ", United Kingdom")
            street_address = addr.street_address_1 or ""
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            hours = list(bs(_["wsl_description"], "lxml").stripped_strings)
            if hours:
                hours = hours[1:]
            yield SgRecord(
                page_url=base_url,
                store_number=_["wsl_id"],
                location_name=_["wsl_name"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["wsl_latitude"],
                longitude=_["wsl_longitude"],
                country_code=_["wsl_country"],
                phone=_["wsl_phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["wsl_street"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

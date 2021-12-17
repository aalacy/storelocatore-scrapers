from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.quiznos.com"
base_url = "https://restaurants.quiznos.com/stores.json?callback=storeList"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers).text.split("storeList(")[1][:-1]
        )
        for _ in locations:
            street_address = _["address1"]
            if _["address2"]:
                street_address += " " + _["address2"]
            phone = _["phone"]
            if phone:
                phone = phone.split("Ext")[0].strip()
            yield SgRecord(
                page_url=base_url,
                store_number=_["storeid"],
                location_name=_["restaurantname"],
                street_address=street_address,
                city=_["city"],
                state=_["statecode"],
                zip_postal=_["zipcode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code="US",
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=_["businesshours"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

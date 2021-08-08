from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://kfc.com.mx"
base_url = "https://kfc.com.mx/find-a-kfc"

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var allRestDetails =")[1]
            .split("var storeDetails")[0]
            .strip()[1:-2]
        )
        for _ in locations:
            street_address = _["AddressLine1"]
            if _["AddressLine2"]:
                street_address += " " + _["AddressLine2"]
            hours = []
            for hh in _["Hours"]:
                hours.append(f"{days[hh['Day']]}: {hh['OpenTime']}-{hh['CloseTime']}")
            page_url = (
                f"https://kfc.com.mx/store?latitude={_['Lat']}&longitude={_['Long']}"
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["RestaurantId"],
                location_name=_["RestaurantName"],
                street_address=street_address,
                city=_["City"],
                state=_["Province"],
                zip_postal=_["PostalCode"],
                latitude=_["Lat"],
                longitude=_["Long"],
                country_code="Mexico",
                phone=_["PhoneNo"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

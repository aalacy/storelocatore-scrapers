from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.racetrac.com"
base_url = "https://www.racetrac.com/locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var storedata =")[1]
            .split("</script>")[0]
            .strip()[:-1]
        )
        for _ in locations:
            street_address = _["StoreAddress1"]
            if _["StoreAddress2"]:
                street_address += " " + _["StoreAddress2"]
            hours_of_operation = ""
            if _["Is24Hours"]:
                hours_of_operation = "24 Hours / 7 Days"
            page_url = f"https://www.racetrac.com/Locations/Detail/{_['StoreNumber']}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["StoreNumber"],
                location_name=_["StoreName"],
                street_address=street_address,
                city=_["StoreCity"],
                state=_["StoreState"],
                zip_postal=_["StoreZipCode"],
                latitude=_["StoreLatitude"],
                longitude=_["StoreLongitude"],
                country_code="US",
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pizzahut.lk"
base_url = "https://www.pizzahut.lk/outlet/selectoutlets"


def fetch_data():
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers).json()
        for _ in locations:
            coord = _["Point"].split("(")[1][:-1].split(" ")
            raw_address = (
                _["Address"].replace("\n", "").split("(")[0].strip().replace("–", "-")
            )
            yield SgRecord(
                page_url="https://www.pizzahut.lk/Locations.aspx",
                store_number=_["Id"],
                location_name=_["Name"],
                street_address=", ".join(raw_address.split(",")[:-1]).strip(),
                city=raw_address.split(",")[-1].replace(".", "").strip(),
                latitude=coord[1],
                longitude=coord[0],
                country_code="Sri Lanka",
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

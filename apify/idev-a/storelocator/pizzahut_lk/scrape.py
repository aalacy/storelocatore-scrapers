from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "origin": "https://www.pizzahut.lk",
    "referer": "https://www.pizzahut.lk",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.pizzahut.lk"
base_url = "https://www.pizzahut.lk/outlet/selectoutlets"


def fetch_data():
    with SgRequests() as session:
        locations = session.post(base_url, headers=_headers).json()
        for _ in locations:
            try:
                coord = _["Point"].split("(")[1][:-1].split(" ")
            except:
                coord = ["", ""]

            raw_address = (
                _["Address"]
                .replace("\n", "")
                .replace("\r", "")
                .split("(")[0]
                .strip()
                .replace("–", "-")
            )
            addr = raw_address.split(",")
            yield SgRecord(
                page_url="https://www.pizzahut.lk/Locations.aspx",
                store_number=_["Id"],
                location_name=_["Name"],
                street_address=", ".join(addr[:-1]).strip(),
                city=addr[-1].replace(".", "").strip(),
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

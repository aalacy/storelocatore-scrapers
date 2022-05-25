from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.4fingers.com.sg"
base_url = "https://www.4fingers.com.sg/wp-admin/admin-ajax.php?action=store_search&lat=1.3292466&lng=103.8689931&max_results=25&search_radius=50&autoload=1"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["store_data"]
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            if _["short_content"]:
                hours = list(bs(_["short_content"], "lxml").stripped_strings)
            yield SgRecord(
                page_url="https://www.4fingers.com.sg/locate-us/",
                store_number=_["id"],
                location_name=_["store"],
                street_address=street_address,
                city=_["city"],
                state=_.get("state"),
                zip_postal=_["zip"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="SG",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours).replace("Breakfast Timing:", ""),
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

locator_domain = "https://www.charterfitness.com/"
json_url = "https://cfxfit.com/wp-admin/admin-ajax.php?action=store_search&lat=41.94045&lng=-88.14836&max_results=500&search_radius=5000&autoload=1"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(json_url).json()
        for _ in locations:
            street_address = _.get("address")
            if _.get("address2"):
                street_address += " " + _.get("address2")
            hours = []
            for hh in bs(_["hours"], "lxml").select("table tr"):
                hours.append(": ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=_.get("permalink"),
                store_number=_["id"],
                location_name=_.get("store"),
                street_address=street_address,
                city=_.get("city"),
                state=_.get("state"),
                zip_postal=_.get("zip"),
                country_code=_.get("country", "USA"),
                phone=_["phone"],
                locator_domain=locator_domain,
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation="; ".join(hours).replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

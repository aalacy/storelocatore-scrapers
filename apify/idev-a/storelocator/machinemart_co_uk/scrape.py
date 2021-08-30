from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

base_url = "https://www.machinemart.co.uk/customactions/storefindersurface/GetStores/"
locator_domain = "https://www.machinemart.co.uk"


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(base_url).json()["Stores"]
        for store in store_list:
            page_url = "https://www.machinemart.co.uk/stores/" + store["id"]
            sp1 = bs(session.get(page_url).text, "lxml")
            hours = sp1.select_one("div.times p").contents[2:]
            hours = [x.string for x in hours if x.string is not None]

            yield SgRecord(
                page_url=page_url,
                location_name=store["name"],
                street_address=store["addressLine1"],
                city=store["addressLine2"],
                zip_postal=store["addressLine4"],
                country_code="UK",
                phone=store["telephoneNumber"].replace("\n", ""),
                locator_domain=locator_domain,
                latitude=store["latitude"],
                longitude=store["longitude"],
                hours_of_operation=" ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

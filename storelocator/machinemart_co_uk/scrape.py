from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("machinemart")

base_url = "https://www.machinemart.co.uk/customactions/storefindersurface/GetStores/"
locator_domain = "https://www.machinemart.co.uk"


def fetch_data():
    with SgRequests() as session:
        store_list = session.get(base_url).json()["Stores"]
        for store in store_list:
            page_url = "https://www.machinemart.co.uk/stores/" + store["id"] + "/"
            logger.info(page_url)
            sp1 = bs(session.get(page_url).text, "lxml")
            hours = sp1.select_one("div.times p").contents[2:]
            pp = sp1.select("div.times p")
            if len(pp) > 1:
                if pp[-1].select("u"):
                    del pp[-1]
                hours = list(pp[-1].stripped_strings)

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
                raw_address=" ".join(sp1.select_one("div.address").stripped_strings),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

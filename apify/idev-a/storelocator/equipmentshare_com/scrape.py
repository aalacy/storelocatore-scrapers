from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("equipmentshare")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.equipmentshare.com/"
    base_url = "https://api.storepoint.co/v1/15f1f09aceabf7/locations?lat=33.956&long=-118.3887&radius=3000"
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations["results"]["locations"]:
            addr = parse_address_intl(_["streetaddress"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2

            hours = []
            page_url = ""
            if _["website"]:
                page_url = "https://www." + _["website"]
                logger.info(page_url)
                hours = [
                    ": ".join(hh.stripped_strings)
                    for hh in bs(
                        session.get(page_url, headers=_headers).text, "lxml"
                    ).select("div.hours-box div.day-row")
                ]
            yield SgRecord(
                page_url=page_url,
                location_name=_["name"],
                store_number=_["id"],
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                latitude=_["loc_lat"],
                longitude=_["loc_long"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=_["streetaddress"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

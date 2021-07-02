from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgpostal import parse_address_intl

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
                page_url = "https://" + _["website"]
                logger.info(page_url)
                try:
                    ss = json.loads(
                        bs(session.get(page_url, headers=_headers).text, "lxml")
                        .find("script", type="application/ld+json")
                        .string
                    )
                    hours = ss["openingHoursSpecification"]["dayOfWeek"]["name"]
                except:
                    pass
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
                hours_of_operation=hours,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

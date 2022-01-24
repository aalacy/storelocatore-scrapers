from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("thewarehouse")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thewarehouse.co.nz"
base_url = "https://www.thewarehouse.co.nz/stores"


def fetch_data():
    with SgRequests() as session:
        regions = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "div.region-select select option"
        )
        for region in regions:
            if not region.get("value"):
                continue
            url = f"https://www.thewarehouse.co.nz/on/demandware.store/Sites-twl-Site/default/Stores-FindStores?region={region.get('value')}"
            logger.info(url)
            locations = (
                session.get(url, headers=_headers).json()["stores"].get("stores", [])
            )
            for ss in locations:
                street_address = ss["address1"]
                if ss["address2"]:
                    street_address += " " + ss["address2"]
                hours = json.loads(ss["storeHoursJson"]).get("openingHours", [])
                page_url = f"https://www.thewarehouse.co.nz/stores/store-details?StoreID={ss['ID']}"
                yield SgRecord(
                    page_url=page_url,
                    store_number=ss["ID"],
                    location_name=ss["name"],
                    street_address=street_address.replace("The Warehouse", "").replace(
                        ",", ""
                    ),
                    city=ss["city"],
                    state=ss["stateCode"],
                    zip_postal=ss["postalCode"],
                    country_code="NZ",
                    phone=ss["phone"],
                    latitude=ss["latitude"],
                    longitude=ss["longitude"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                    raw_address=ss["fullAddress"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

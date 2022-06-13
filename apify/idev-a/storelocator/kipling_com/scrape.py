from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kipling")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.kipling-usa.com"
base_url = "https://www.kipling-usa.com/stores"
json_url = "https://www.kipling-usa.com/on/demandware.store/Sites-kip-Site/default/Stores-GetNearestStores?state={}&countryCode=&onlyCountry=true&retailstores=true&outletstores=true"


def fetch_data():
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select#dwfrm_storelocator_states_stateUSCA option"
        )
        for state in states:
            if not state.get("value"):
                continue
            locations = session.get(
                json_url.format(state["value"]), headers=_headers
            ).json()
            logger.info(f"{state['value']} {len(locations)}")
            for key, _ in locations.items():
                street_address = _["address1"]
                if _["address2"]:
                    street_address += " " + _["address2"]
                page_url = (
                    f"https://www.kipling-usa.com/store-details?storeid={_['storeID']}"
                )
                yield SgRecord(
                    page_url=page_url,
                    store_number=_["storeID"],
                    location_name=_["name"],
                    street_address=street_address,
                    city=_["city"],
                    state=_["stateCode"],
                    zip_postal=_["postalCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code=_["countryCode"],
                    phone=_["phone"],
                    location_type=_["department"],
                    locator_domain=locator_domain,
                    hours_of_operation=_["storeHours"].replace(",", ";"),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

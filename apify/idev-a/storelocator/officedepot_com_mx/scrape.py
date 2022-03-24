from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("officedepot")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.officedepot.com.mx"
base_url = "https://www.officedepot.com.mx/officedepot/en/store-finder"
json_url = "https://www.officedepot.com.mx/officedepot/en/store-finder?q={}&page={}"


def fetch_data():
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "select.js-state-store-finder-search-select option"
        )
        for state in states:
            if not state.get("value"):
                continue
            page = 0
            locations = session.get(
                json_url.format(state["value"], page), headers=_headers
            ).json()["data"]
            logger.info(f"[{state['value']}] {len(locations)}")
            for _ in locations:
                hours = []
                for day, times in _.get("openings", {}).items():
                    hours.append(f"{day}: {times}")
                street_address = _["line1"]
                if _.get("line2"):
                    street_address += " " + _["line2"]
                yield SgRecord(
                    page_url=base_url,
                    store_number=_["name"],
                    location_name="SHOP - " + _["displayName"],
                    street_address=street_address,
                    city=_["town"],
                    zip_postal=_["postalCode"],
                    latitude=_["latitude"],
                    longitude=_["longitude"],
                    country_code="Mexico",
                    phone=_["phone"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

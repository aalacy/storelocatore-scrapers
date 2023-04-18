from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("tgscolorado")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://tgscolorado.com/"
    base_url = "https://tgscolorado.com/stores"
    with SgRequests() as session:
        soup = bs(session.get(base_url).text, "lxml")
        json_body = json.loads(
            soup.find("script", type="application/json").string.strip()
        )
        for key, _ in (
            json_body.get("hydrate", {})
            .get("stores", {})
            .get("view_fields", {})
            .items()
        ):
            page_url = f"https://www.tgscolorado.com/stores/{_['field_store_code']}"
            logger.info(page_url)
            location_type = ""
            if "Temporarily Closed" in _["field_store_status"]:
                location_type = "Temporarily Closed"
            _hr = bs(session.get(page_url).text, "lxml").find(
                "h4", string=re.compile(r"Regular Store Hours")
            )
            hours_of_operation = ""
            if _hr:
                hours_of_operation = _hr.find_next_sibling().text.strip()
            yield SgRecord(
                page_url=page_url,
                store_number=_["field_store_id"],
                location_name=_["title"].strip(),
                street_address=_["field_store_address_address_line1"]
                .replace("&amp;", "&")
                .strip(),
                city=_["field_store_address_locality"],
                state=_["field_store_address_administrative_area"],
                zip_postal=_["field_store_address_postal_code"],
                latitude=_["field_store_geolocation"].split(",")[0].strip(),
                longitude=_["field_store_geolocation"].split(",")[1].strip(),
                country_code=_["field_store_address_country_code"],
                phone=_["field_store_telephone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

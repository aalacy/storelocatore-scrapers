from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("valleystorageco")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.valleystorageco.com"
base_url = "https://www.valleystorageco.com/locations/"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            session.get(base_url, headers=_headers)
            .text.split("var candee_js_variables     =")[1]
            .split("if (")[0]
            .strip()[:-1]
        )["facilities"]
        for _ in locations:
            page_url = _["permalink"]
            logger.info(page_url)
            sp1 = bs(session.get(page_url, headers=_headers).text, "lxml")
            hours = []
            for hh in sp1.select_one("div.content-hours ul").select("li"):
                hours.append(" ".join(hh.stripped_strings))
            yield SgRecord(
                page_url=page_url,
                store_number=_["prop_id"],
                location_name=_["facility_name"],
                street_address=_["facility_address"],
                city=_["facility_city"],
                state=_["facility_region"],
                zip_postal=_["facility_zipcode"],
                country_code=_["facility_country"],
                phone=_["facility_phone"],
                latitude=_["lat"],
                longitude=_["lng"],
                hours_of_operation="; ".join(hours),
                locator_domain=locator_domain,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

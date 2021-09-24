from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("phoenix")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.phoenix.edu"
loc_url = "https://www.phoenix.edu/campus-locations.html"
base_url = "https://www.phoenix.edu/api/plct/3/uopx/locations?type=site&page.size=500"


def fetch_data():
    with SgRequests() as session:
        hours_of_operation = ""
        sp1 = bs(session.get(loc_url, headers=_headers).text, "lxml")
        ss = json.loads(
            sp1.select_one("div.react-campusdetailhero-container")[
                "data-json-properties"
            ]
            .replace("&#34;", '"')
            .replace("&lt;", "<")
            .replace("&gt;", ">")
        )
        if ss["campusData"].get("hours"):
            hours_of_operation = "; ".join(
                bs(ss["campusData"]["hours"], "lxml").stripped_strings
            )
            if "temporarily closed" in hours_of_operation:
                hours_of_operation = "temporarily closed"
        locations = session.get(base_url, headers=_headers).json()["results"]
        for loc in locations:
            _ = loc["attributes"]
            street_address = _["addressLine2"]
            if _.get("addressLine3"):
                street_address += " " + _["addressLine3"]
            phone = _.get("phoneLocal")
            if not phone:
                phone = _.get("phoneTollFree")
            yield SgRecord(
                page_url=loc_url,
                location_name=_["altName"],
                street_address=street_address,
                city=_["city"],
                state=_["stateProvince"],
                zip_postal=_["postalCode"],
                latitude=_["latitude"],
                longitude=_["longitude"],
                country_code=loc["countryCode"],
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

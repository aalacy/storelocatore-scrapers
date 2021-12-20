from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("waterfields")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.waterfields-bakers.co.uk"
base_url = "https://www.waterfields-bakers.co.uk/ajax/StoresLocator.asp?latitude=53.494655&longitude=-2.489626"


def fetch_records(http):
    locations = bs(http.get(base_url, headers=_headers).text, "lxml").select("marker")
    for _ in locations:
        street_address = _["address"]
        if _.get("address2"):
            street_address += " " + _["address2"]
        yield SgRecord(
            page_url="https://www.waterfields-bakers.co.uk/branchfinder",
            location_name=_["name"],
            street_address=street_address,
            city=_["city"],
            zip_postal=_["postcode"],
            country_code="UK",
            phone=_["phone"],
            latitude=_["lat"],
            longitude=_["lng"],
            locator_domain=locator_domain,
            hours_of_operation=_["openingtimes"].replace("\r\n", "; "),
        )


if __name__ == "__main__":
    with SgRequests() as http:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
            for rec in fetch_records(http):
                writer.write_row(rec)

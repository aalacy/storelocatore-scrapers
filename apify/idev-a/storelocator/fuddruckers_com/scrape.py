from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("fuddruckers")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.fuddruckers.com"
base_url = "https://www.fuddruckers.com/services/location/get_stores_by_position.php"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["places"][
            "positions"
        ]["data"]
        for _ in locations:
            page_url = locator_domain + _["link"]
            logger.info(page_url)
            title = bs(session.get(page_url, headers=_headers).text, "lxml").select_one(
                "div.store-hours-title"
            )
            location_type = ""
            if title and "temporarily closed" in title.text.lower():
                location_type = "temporarily closed"
            zip_postal = _["zip"]
            if zip_postal == "N/A":
                zip_postal = ""
            yield SgRecord(
                page_url=page_url,
                store_number=_["id"],
                location_name=_["storename"],
                street_address=_["address"],
                city=_["city"],
                state=_["state"],
                zip_postal=zip_postal,
                latitude=_["lat"],
                longitude=_["lng"],
                country_code=_["country"],
                phone=_["phone"],
                location_type=location_type,
                locator_domain=locator_domain,
                hours_of_operation=_["hours"],
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

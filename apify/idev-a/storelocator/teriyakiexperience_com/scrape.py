from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.teriyakiexperience.com/"
base_url = "https://www.teriyakiexperience.com/wp-admin/admin-ajax.php?action=get_google_map_data&query="


def fetch_data():
    with SgRequests() as session:
        links = session.get(base_url, headers=_headers).json()["data"]
        for link in links:
            _ = link["info"]
            location_name = _["post_title"]
            location_type = ""
            if "temporarily closed" in location_name.lower():
                location_type = "Temporarily Closed"

            logger.info(_["permalink"])
            sp1 = bs(session.get(_["permalink"], headers=_headers).text, "lxml")
            city = state = zip_postal = ""
            for aa in sp1.select("div.location-container ul.list-unstyled li"):
                addr = aa.text.split(":")[-1].strip()
                if "City" in aa.text:
                    city = addr.split(",")[0].strip()
                    zip_postal = addr.split(",")[1].strip()
                if "Province" in aa.text:
                    state = addr

            yield SgRecord(
                page_url=_["permalink"],
                store_number=_["ID"],
                location_name=_["post_title"],
                street_address=_["street"],
                city=city,
                zip_postal=zip_postal.replace("Costa Rica", "")
                .replace("Georgia", "")
                .strip(),
                state=state,
                country_code=_["country"]["name"],
                phone=_["contact"]["phone"],
                locator_domain=locator_domain,
                latitude=link["position"]["lat"],
                longitude=link["position"]["lng"],
                location_type=location_type,
                hours_of_operation="; ".join(
                    bs(_["contact"]["hours"], "lxml").stripped_strings
                ).replace(",", ";"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

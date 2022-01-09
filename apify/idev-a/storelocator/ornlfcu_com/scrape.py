from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ornlfcu.com/"
base_url = "https://www.ornlfcu.com/locations"


def fetch_data():
    with SgRequests() as session:
        locations = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("input#hdnLocations")["value"]
            .replace("&quot;", '"')
        )
        for _ in locations:
            addr = _["Location"]
            hours = [
                hh.text.strip().replace("&ndash;", "-")
                for hh in bs(_["LobbyHours"], "lxml").select("ul li")
            ]
            page_url = f"https://www.ornlfcu.com/locations/location-detail/{addr['City'].lower()}-{_['LocationType'].lower()}"
            yield SgRecord(
                page_url=page_url,
                store_number=_["BranchId"],
                location_name=_["Name"],
                street_address=addr["Street"],
                city=addr["City"],
                state=addr["State"],
                zip_postal=addr["ZipCode"],
                latitude=addr["Latitude"],
                longitude=addr["Longitude"],
                country_code=addr["Country"],
                location_type=_["LocationType"],
                phone=_["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours)
                .replace("\u2060", "")
                .replace("–", "-"),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

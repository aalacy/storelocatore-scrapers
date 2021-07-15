from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID, RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import dirtyjson as json
import re

logger = SgLogSetup().get_logger("premiertruck")


_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.premiertruck.com"
base_url = "https://images.motorcar.com/fonts/dealerlocator/data/locations.json"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        url = locator_domain + locations[0]["web"]
        sp1 = bs(session.get(url, headers=_headers).text, "lxml")
        locs = sp1.find("script", string=re.compile(r"var loc_")).string.split(
            "var loc_"
        )
        for loc in locs:
            if not loc:
                continue
            _ = json.loads(loc.split("=")[1].split(";")[0].strip())
            page_url = locator_domain + f"/{_['locAddress']['City']}.aspx"
            street_address = _["locAddress"]["Address1"]
            if _["locAddress"].get("address2"):
                street_address += " " + _["locAddress"]["Address2"]
            hours = []
            for day, hh in _["Hours"]["General"].items():
                hours.append(f"{day}: {hh}")
            latitude = _["locAddress"]["GeoLat"]
            longitude = _["locAddress"]["GeoLong"]
            if latitude == "0":
                latitude = ""
            if longitude == "0":
                longitude = ""
            yield SgRecord(
                page_url=page_url,
                store_number=_["locAccountID"],
                location_name=_["locName"],
                street_address=street_address,
                city=_["locAddress"]["City"],
                state=_["locAddress"]["State"],
                zip_postal=_["locAddress"]["Zip"],
                latitude=latitude,
                longitude=longitude,
                country_code=_["locAddress"]["Country"],
                phone=_["Contacts"]["General"]["Phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

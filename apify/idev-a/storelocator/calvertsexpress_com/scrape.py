from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://calvertsexpress.com"
base_url = "https://calvertsexpress.com/data/locations.xml?formattedAddress=&boundsNorthEast=&boundsSouthWest="


def fetch_data():
    with SgRequests() as session:
        locations = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "marker"
        )
        for _ in locations:
            street_address = _["address"]
            if _["address2"]:
                street_address += " " + _["address2"]
            hours = []
            location_name = _["name"]
            if "TEMPORARILY CLOSED" in location_name:
                location_name = location_name.split("-")[0].strip()
                hours = ["TEMPORARILY CLOSED"]
            else:
                hours.append(f"Mon - Fri: {_['hours1']}")
                hours.append(f"Sat: {_['hours2']}")
                hours.append(f"Sun: {_['hours3']}")
            yield SgRecord(
                page_url=_["web"],
                location_name=location_name,
                street_address=street_address,
                city=_["city"],
                state=_["state"],
                zip_postal=_["postal"],
                latitude=_["lat"],
                longitude=_["lng"],
                country_code="US",
                phone=_["phone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

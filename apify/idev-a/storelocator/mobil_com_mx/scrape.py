from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.mobil.com.mx"
base_url = "https://www.mobil.com.mx/es-MX/api/locator/Locations?Latitude1=20.563321313278717&Latitude2=20.64366209872576&Longitude1=-100.4843057862854&Longitude2=-100.3325142137146&DataSource=RetailGasStations&Country=MX&Customsort=False)"


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()
        for _ in locations:
            street_address = _["AddressLine1"]
            if _["AddressLine2"]:
                street_address += " " + _["AddressLine2"]

            hours = []
            if _["WeeklyOperatingHours"]:
                hours = bs(_["WeeklyOperatingHours"], "lxml").stripped_strings
            page_url = (
                locator_domain
                + f"/en-MX/find-station/{_['Brand'].lower()}-{_['City'].lower().replace(' ','')}-{_['StateProvince'].lower()}-{_['LocationName'].lower().replace('(','').replace(')', '')}-{_['LocationID']}"
            )
            yield SgRecord(
                page_url=page_url,
                store_number=_["LocationID"],
                location_name=_["LocationName"],
                street_address=street_address,
                city=_["City"],
                state=_["StateProvince"],
                zip_postal=_["PostalCode"],
                latitude=_["Latitude"],
                longitude=_["Longitude"],
                country_code=_["Country"],
                phone=_["Telephone"],
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

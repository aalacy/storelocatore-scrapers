from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://guam.mobil.com"
urls = {
    "Guam": "https://guam.mobil.com/en-GU/api/locator/Locations?Latitude1=13.137523887013367&Latitude2=13.80527304618928&Longitude1=144.1764495449707&Longitude2=145.3022048550293&DataSource=RetailGasStations&Country=GU&Customsort=False",
    "Saipan": "https://saipan.mobil.com/en-MP/api/locator/Locations?Latitude1=14.858898338157513&Latitude2=15.521549050165852&Longitude1=145.12695484497067&Longitude2=146.25271015502926&DataSource=RetailGasStations&Country=MP&Customsort=False",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = _["AddressLine1"]
                if _["AddressLine2"]:
                    street_address += " " + _["AddressLine2"]
                hours = []
                if _["WeeklyOperatingHours"]:
                    hours = bs(_["WeeklyOperatingHours"], "lxml").stripped_strings
                if _["Country"] == "MP":
                    page_url = f"https://saipan.mobil.com/en-mp/find-station/{_['Brand'].lower()}-{_['City'].lower().replace(' ','')}-{_['LocationName'].lower().replace('(','').replace(')', '').replace(' ', '')}-{_['LocationID']}"
                else:
                    page_url = (
                        locator_domain
                        + f"/en-au/find-station/{_['Brand'].lower()}-{_['City'].lower().replace(' ','')}-{_['StateProvince'].lower()}-{_['LocationName'].lower().replace('(','').replace(')', '').replace(' ', '')}-{_['LocationID']}"
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
                    country_code=country,
                    phone=_["Telephone"],
                    location_type=_["Brand"],
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

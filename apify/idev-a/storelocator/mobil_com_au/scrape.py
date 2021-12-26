from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://mobil.com.au"
urls = {
    "New Zealand": "https://www.mobil.co.nz/en-NZ/api/locator/Locations?Latitude1=-63.84287216784316&Latitude2=4.253783352802964&Longitude1=102.71499615625001&Longitude2=-113.18832415625002&DataSource=RetailGasStations&Country=NZ&Customsort=False",
    "Australia": "https://www.mobil.com.au/en-AU/api/locator/Locations?Latitude1=-76.87482970882189&Latitude2=45.96935274325634&Longitude1=6.835295062500006&Longitude2=-64.97134556250006&DataSource=RetailGasStations&Country=AU&Customsort=True",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = _["AddressLine1"]
                if _["Country"] == "AU":
                    page_url = (
                        locator_domain
                        + f"/en-au/find-station/{_['Brand'].lower()}-{_['City'].lower().replace(' ','')}-{_['StateProvince'].lower()}-{_['LocationName'].lower().replace('(','').replace(')', '')}-{_['LocationID']}"
                    )
                else:
                    page_url = f"https://www.mobil.co.nz/en-au/find-station/{_['Brand'].lower()}-{_['City'].lower().replace(' ','')}-{_['StateProvince'].lower()}-{_['LocationName'].lower().replace('(','').replace(')', '')}-{_['LocationID']}"
                phone = _["Telephone"]
                if phone == "NA":
                    phone = ""
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
                    phone=phone,
                    location_type=_["Brand"],
                    locator_domain=locator_domain,
                    hours_of_operation=_["WeeklyOperatingHours"],
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

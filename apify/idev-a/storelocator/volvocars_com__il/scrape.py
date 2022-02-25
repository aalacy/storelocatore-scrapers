from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.volvocars.com/il"
base_url = ""
urls = {
    "Israel": "https://www.volvocars.com/data/retailer?countryCode=IL&languageCode=HE&northToSouthSearch=True&serviceType=Sales&isOxp=False&sc_site=il",
    "Bularia": "https://www.volvocars.com/data/retailer?countryCode=BG&languageCode=bg&northToSouthSearch=False&capability=&isOxp=True&sc_site=bg",
    "Romania": "https://www.volvocars.com/data/retailer?countryCode=RO&languageCode=RO&northToSouthSearch=False&serviceType=Sales&isOxp=False&sc_site=ro",
    "Rusia": "https://www.volvocars.com/data/retailer?countryCode=RU&languageCode=RU&northToSouthSearch=False&capability=&isOxp=False&sc_site=ru",
    "Moldova": "https://www.volvocars.com/data/retailer?countryCode=MD&languageCode=RO&northToSouthSearch=False&serviceType=Sales&isOxp=False&sc_site=ro-md",
}


def fetch_data():
    with SgRequests() as session:
        for country, base_url in urls.items():
            locations = session.get(base_url, headers=_headers).json()
            for _ in locations:
                street_address = _["AddressLine1"]
                hours = []
                for hr in _["Services"]:
                    if hr["ServiceType"] == "new_car_sales" and hr["OpeningHours"]:
                        hours.append(hr["OpeningHours"])

                yield SgRecord(
                    store_number=_["DealerId"],
                    location_name=_["Name"],
                    street_address=street_address,
                    city=_["City"],
                    state=_["District"],
                    zip_postal=_["ZipCode"],
                    latitude=_["GeoCode"]["Latitude"],
                    longitude=_["GeoCode"]["Longitude"],
                    country_code=_["Country"],
                    phone=_["Phone"],
                    locator_domain=locator_domain,
                    location_type=_["ServiceType"],
                    hours_of_operation="; ".join(hours).replace("Sales:", ""),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

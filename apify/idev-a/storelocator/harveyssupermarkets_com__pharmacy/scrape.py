from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from sgrequests.sgrequests import SgRequests

logger = SgLogSetup().get_logger("harveyssupermarkets")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.harveyssupermarkets.com/pharmacy"
base_url = "https://www.harveyssupermarkets.com/V2/storelocator/getStores?search=32216&strDefaultMiles=5000&filter=Pharmacy"


def fetch_records():
    with SgRequests() as http:
        locations = http.get(base_url, headers=_headers).json()
        for _ in locations:
            addr = _["Address"]
            street_address = addr["AddressLine1"]
            if addr["AddressLine2"]:
                street_address += " " + addr["AddressLine2"]
            page_url = f"https://www.harveyssupermarkets.com/storedetails/{addr['City']}/{addr['State']}/?search={_['StoreCode']}&zipcode={addr['Zipcode']}"
            yield SgRecord(
                page_url=page_url,
                location_name=f"Harveys at {street_address}",
                store_number=_["StoreCode"],
                street_address=street_address,
                city=addr["City"],
                state=addr["State"],
                zip_postal=addr["Zipcode"],
                country_code=addr["Country"],
                phone=_["Phone"],
                latitude=addr["Latitude"],
                longitude=addr["Longitude"],
                locator_domain=locator_domain,
                hours_of_operation=_["WorkingHours"].replace(",", "; "),
            )


if __name__ == "__main__":
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_records():
            writer.write_row(rec)

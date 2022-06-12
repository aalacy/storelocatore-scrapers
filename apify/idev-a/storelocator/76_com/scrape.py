from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import us
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


logger = SgLogSetup().get_logger("76")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.76.com/"
base_url = "https://www.76.com/bin/stationfinderservlet?s=psx_76"

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])


def get_country_by_code(code=""):
    if us.states.lookup(code):
        return "US"
    else:
        return "MX"


def fetch_data():
    with SgRequests() as session:
        credential = session.get(base_url, headers=_headers).json()["credentials"]
        maxZ = search.items_remaining()
        total = 0
        for lat, lng in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            if lat < 0:
                continue
            logger.info(("Pulling Geo Code %s..." % lat, lng))
            url = f"https://spatial.virtualearth.net/REST/v1/data/a1ed23772f5f4994a096eaa782d07cfb/US_BrandedSites/Sites?spatialFilter=nearby({lat},{lng},500.0)&$filter=Confidence%20Eq%20%27High%27%20And%20(EntityType%20Eq%20%27Address%27%20Or%20EntityType%20Eq%20%27RoadIntersection%27)%20AND%20(Brand%20eq%20%27U76%27%20OR%20Brand%20Eq%20%27U76%27%20OR%20Brand%20Eq%20%27CON%27%20OR%20Brand%20Eq%20%27P66%27)&$format=json&$inlinecount=allpages&$select=*,__Distance&key={credential}&$top=300"

            try:
                locations = session.get(url, headers=_headers).json()["d"]["results"]
            except:
                continue
            total += len(locations)
            for store in locations:
                search.found_location_at(store["Latitude"], store["Longitude"])
                page_url = (
                    "https://www.76.com/station/"
                    + store["Brand"]
                    + "-"
                    + store["Name"].replace(" ", "-")
                    + "-"
                    + store["EntityID"]
                )
                phone = store["Phone"]
                if phone == "0000000000":
                    phone = ""
                yield SgRecord(
                    page_url=page_url,
                    store_number=store["EntityID"],
                    location_name=store["Name"],
                    street_address=store["AddressLine"],
                    city=store["Locality"],
                    state=store["AdminDistrict"],
                    zip_postal=store["PostalCode"],
                    latitude=store["Latitude"],
                    longitude=store["Longitude"],
                    country_code=get_country_by_code(store["AdminDistrict"]),
                    phone=phone,
                    location_type=store["Brand"],
                    locator_domain=locator_domain,
                )
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

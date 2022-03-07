from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import us


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
            if locations:
                search.found_location_at(lat, lng)
            for store in locations:

                store["page_url"] = (
                    "https://www.76.com/station/"
                    + store["Brand"]
                    + "-"
                    + store["Name"].replace(" ", "-")
                    + "-"
                    + store["EntityID"]
                )
                store["Phone"] = store["Phone"] or "<MISSING>"
                store["country"] = get_country_by_code(store["AdminDistrict"])
                yield store
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["Name"],
        ),
        latitude=sp.MappingField(
            mapping=["Latitude"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["Longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["AddressLine"],
        ),
        city=sp.MappingField(
            mapping=["Locality"],
        ),
        state=sp.MappingField(
            mapping=["AdminDistrict"],
        ),
        zipcode=sp.MappingField(
            mapping=["PostalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["Phone"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MissingField(),
        store_number=sp.MappingField(
            mapping=["EntityID"],
        ),
        location_type=sp.MappingField(
            mapping=["Brand"],
        ),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
        duplicate_streak_failure_factor=1000,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


session = SgRequests()
website = "floridatile_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "Referer": "https://www.floridatile.com/store-locator/",
    "X-CSRFToken": "haPUjfbIdmWdMLaagkZfBOvQK0J3EkOEhmgqpGqpgr5MVbim6w2xQFxZDbAGikOR",
    "Cookie": "csrftoken=haPUjfbIdmWdMLaagkZfBOvQK0J3EkOEhmgqpGqpgr5MVbim6w2xQFxZDbAGikOR",
}


DOMAIN = "https://www.floridatile.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=500
        )
        for lat, lng in search:
            payload = {
                "operationName": "searchLocations",
                "query": "query searchLocations($before: String, $after: String, $first: Int, $last: Int, $latitude: Float!, $longitude: Float!, $miles: Int!, $locationTypes: [String]!) {\n  searchLocations(before: $before, after: $after, first: $first, last: $last, latitude: $latitude, longitude: $longitude, miles: $miles, locationTypes: $locationTypes) {\n    edges {\n      node {\n        id\n        name\n        dealerId\n        address\n        city\n        state\n        zipCode\n        country\n        phone\n        point\n        fullAddress\n        website\n        locationType\n        distance\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      hasPreviousPage\n      startCursor\n      endCursor\n      __typename\n    }\n    __typename\n  }\n}\n",
                "variables": {
                    "first": 1500,
                    "latitude": lat,
                    "locationTypes": ["Florida Tile", "Distributor", "Dealer"],
                    "longitude": lng,
                    "miles": 500,
                },
            }

            search_url = "https://www.floridatile.com/graphql"
            stores_req = session.post(search_url, headers=headers, json=payload).json()
            for store in stores_req["data"]["searchLocations"]["edges"]:
                title = store["node"]["name"]
                street = store["node"]["address"]
                city = store["node"]["city"]
                state = store["node"]["state"]
                pcode = store["node"]["zipCode"]
                country = store["node"]["country"]
                phone = store["node"]["phone"]
                coords = store["node"]["point"]["coordinates"]
                lat = coords[0]
                lng = coords[1]
                loc_type = store["node"]["locationType"]
                if country == "Canada":
                    country = "CA"

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=DOMAIN,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code=country,
                    store_number=MISSING,
                    phone=phone,
                    location_type=loc_type,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=MISSING,
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

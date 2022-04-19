import json

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    domain = "orangejulius.com"
    session = SgRequests()

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=25
    )
    for lat, lng in all_coordinates:
        frm = {
            "operationName": "NearbyStores",
            "query": "fragment StoreDetailFields on Store {\n  id\n  storeNo\n  address3\n  city\n  stateProvince\n  postalCode\n  country\n  latitude\n  longitude\n  phone\n  conceptType\n  restaurantId\n  utcOffset\n  supportedTimeModes\n  advanceOrderDays\n  storeHours {\n    calendarType\n    ranges {\n      start\n      end\n      weekday\n      __typename\n    }\n    __typename\n  }\n  minisite {\n    webLinks {\n      isDeliveryPartner\n      description\n      url\n      __typename\n    }\n    hours {\n      calendarType\n      ranges {\n        start\n        end\n        weekday\n        __typename\n      }\n      __typename\n    }\n    amenities {\n      description\n      featureId\n      __typename\n    }\n    __typename\n  }\n  flags {\n    blizzardFanClubFlag\n    brazierFlag\n    breakfastFlag\n    cakesFlag\n    canPickup\n    comingSoonFlag\n    creditCardFlag\n    curbSideFlag\n    deliveryFlag\n    driveThruFlag\n    foodAndTreatsFlag\n    giftCardsFlag\n    isAvailableFlag\n    mobileDealsFlag\n    mobileOrderingFlag\n    mtdFlag\n    ojQuenchClubFlag\n    onlineOrderingFlag\n    ojFlag\n    temporarilyClosedFlag\n    __typename\n  }\n  labels {\n    key\n    value\n    __typename\n  }\n  __typename\n}\n\nquery NearbyStores($lat: Float!, $lng: Float!, $country: String!, $searchRadius: Int!) {\n  nearbyStores(\n    lat: $lat\n    lon: $lng\n    country: $country\n    radiusMiles: $searchRadius\n    limit: 50\n    first: 20\n    order: {distance: ASC}\n  ) {\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    nodes {\n      distance\n      distanceType\n      store {\n        ...StoreDetailFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            "variables": {"country": "us", "lat": lat, "lng": lng, "searchRadius": 25},
        }

        hdr = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0",
            "Accept": "*/*",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,partner-platform",
        }
        session.request(
            "https://prod-api.dairyqueen.com/graphql/", method="OPTIONS", headers=hdr
        )
        hdr = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:99.0) Gecko/20100101 Firefox/99.0",
            "Accept": "*/*",
            "Accept-Language": "en-us",
            "Accept-Encoding": "gzip, deflate, br",
            "content-type": "application/json",
            "partner-platform": "Web",
        }
        response = session.post("https://prod-api.dairyqueen.com/graphql/", json=frm, headers=hdr)
        data = json.loads(response.text)
        if not data["data"]["nearbyStores"]:
            continue

        all_locations = data["data"]["nearbyStores"]["nodes"]
        for poi in all_locations:
            poi = poi["store"]
            hoo = []
            if poi['minisite']:
                if poi['minisite']['hours']:
                    for e in poi['minisite']['hours'][0]['ranges']:
                        hoo.append(f'{e["weekday"]}: {e["start"]} - {e["end"]}')
            hoo = ' '.join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.orangejulius.com/en-us/locations/",
                location_name=poi["address3"],
                street_address=poi["address3"],
                city=poi["city"],
                state=poi["stateProvince"],
                zip_postal=poi["postalCode"],
                country_code=poi["country"],
                store_number=poi["storeNo"],
                phone=poi["phone"],
                location_type=poi["conceptType"],
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
            )

            yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()

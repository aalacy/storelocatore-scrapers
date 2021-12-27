import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_2


def fetch_data(coords, sgw):
    lat, lng = coords

    data = {
        "operationName": "getStores",
        "variables": {
            "latitude": float(lat),
            "longitude": float(lng),
            "productId": "",
            "getInventory": False,
            "getProximity": False,
            "numResults": 100,
        },
        "query": "query getStores($latitude: Decimal!, $longitude: Decimal!, $productId: String, $getInventory: Boolean!, $numResults: Int!, $getProximity: Boolean!) {  nearbyStores(filter: {latitude: $latitude, longitude: $longitude, radiusMiles: 10, productId: $productId}, paging: {number: 0, size: $numResults}) {    store {      id      hideTax      online      profile {        name        location {          address          city          isIndoor          latitude          longitude          state          zip          __typename        }        vendor        hasKeypad        canSellMovies        __typename      }      inventory @include(if: $getInventory) {        physicalTitleId        rental        purchase        stock: inStock        defRental        extra        deal: isDeal        isThinned        salePrice        mnp: multiNightPricing {          id          night          price          extraNight          __typename        }        product {          name          __typename        }        __typename      }      __typename    }    proximity @include(if: $getProximity) {      latitude      longitude      dist: distanceMiles      drv: drivingInstructionsAvailable      __typename    }    __typename  }}",
    }

    r = session.post(
        "https://www.redbox.com/gapi/ondemand/hcgraphql/",
        headers=headers,
        data=json.dumps(data),
    )
    js = r.json()["data"]["nearbyStores"]
    if not js:
        return []

    for j in js:
        j = j["store"]
        store_number = j.get("id")
        j = j["profile"]

        a = j.get("location")
        street_address = a.get("address")
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zip")
        country_code = "US"
        location_name = j.get("name") or j.get("vendor")
        latitude = a.get("latitude")
        longitude = a.get("longitude")

        search.found_location_at(latitude, longitude)

        row = SgRecord(
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.redbox.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.redbox.com/locations",
        "content-type": "application/json",
        "x-redbox-device-type": "RedboxWebWindows",
        "Origin": "https://www.redbox.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumAndPageUrlId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        countries = [SearchableCountries.USA]
        search = DynamicGeoSearch(country_codes=countries, granularity=Grain_2())
        for coord in search:
            fetch_data(coord, writer)

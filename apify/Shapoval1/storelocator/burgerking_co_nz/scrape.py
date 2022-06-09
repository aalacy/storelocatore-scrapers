from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.burgerking.co.nz"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "content-type": "application/json",
        "X-Session-Id": "79579fd0-aa7e-4f35-a475-e59d6c337426",
        "x-user-datetime": "2021-12-17T12:37:26+02:00",
        "x-ui-language": "en",
        "x-ui-region": "NZ",
        "Origin": "https://www.burgerking.co.nz",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()

    data = (
        '[{"operationName":"GetRestaurants","variables":{"input":{"filter":"NEARBY","coordinates":{"userLat":'
        + str(lat)
        + ',"userLng":'
        + str(long)
        + ',"searchRadius":25000},"first":20,"status":"OPEN"}},"query":"query GetRestaurants($input: RestaurantsInput) {\\n  restaurants(input: $input) {\\n    pageInfo {\\n      hasNextPage\\n      endCursor\\n      __typename\\n    }\\n    totalCount\\n    nodes {\\n      ...RestaurantNodeFragment\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\\nfragment RestaurantNodeFragment on RestaurantNode {\\n  _id\\n  storeId\\n  isAvailable\\n  posVendor\\n  chaseMerchantId\\n  curbsideHours {\\n    ...OperatingHoursFragment\\n    __typename\\n  }\\n  deliveryHours {\\n    ...OperatingHoursFragment\\n    __typename\\n  }\\n  diningRoomHours {\\n    ...OperatingHoursFragment\\n    __typename\\n  }\\n  distanceInMiles\\n  drinkStationType\\n  driveThruHours {\\n    ...OperatingHoursFragment\\n    __typename\\n  }\\n  driveThruLaneType\\n  email\\n  environment\\n  franchiseGroupId\\n  franchiseGroupName\\n  frontCounterClosed\\n  hasBreakfast\\n  hasBurgersForBreakfast\\n  hasCatering\\n  hasCurbside\\n  hasDelivery\\n  hasDineIn\\n  hasDriveThru\\n  hasMobileOrdering\\n  hasParking\\n  hasPlayground\\n  hasTakeOut\\n  hasWifi\\n  hasLoyalty\\n  id\\n  isDarkKitchen\\n  isFavorite\\n  isHalal\\n  isRecent\\n  latitude\\n  longitude\\n  mobileOrderingStatus\\n  name\\n  number\\n  parkingType\\n  phoneNumber\\n  physicalAddress {\\n    address1\\n    address2\\n    city\\n    country\\n    postalCode\\n    stateProvince\\n    stateProvinceShort\\n    __typename\\n  }\\n  playgroundType\\n  pos {\\n    vendor\\n    __typename\\n  }\\n  posRestaurantId\\n  restaurantImage {\\n    asset {\\n      _id\\n      metadata {\\n        lqip\\n        palette {\\n          dominant {\\n            background\\n            foreground\\n            __typename\\n          }\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    crop {\\n      top\\n      bottom\\n      left\\n      right\\n      __typename\\n    }\\n    hotspot {\\n      height\\n      width\\n      x\\n      y\\n      __typename\\n    }\\n    __typename\\n  }\\n  restaurantPosData {\\n    _id\\n    __typename\\n  }\\n  status\\n  vatNumber\\n  __typename\\n}\\n\\nfragment OperatingHoursFragment on OperatingHours {\\n  friClose\\n  friOpen\\n  monClose\\n  monOpen\\n  satClose\\n  satOpen\\n  sunClose\\n  sunOpen\\n  thrClose\\n  thrOpen\\n  tueClose\\n  tueOpen\\n  wedClose\\n  wedOpen\\n  __typename\\n}\\n"}]'
    )

    r = session.post(
        "https://euc1-prod-bk.rbictg.com/graphql", headers=headers, data=data
    )

    js = r.json()[0]["data"]["restaurants"]["nodes"]

    for j in js:
        a = j.get("physicalAddress")
        ids = j.get("id")
        page_url = f"https://www.burgerking.co.nz/store-locator/store/{ids}"

        location_name = j.get("name")
        street_address = f"{a.get('address1')} {a.get('address2')}".strip()
        if street_address.find("BK ") != -1:
            street_address = " ".join(street_address.split(",")[1:]).strip()
        city = a.get("city")
        state = a.get("stateProvince")
        postal = a.get("postalCode")
        country_code = "NZ"
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("storeId")
        location_type = j.get("__typename")
        days = ["mon", "tue", "wed", "thr", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d.capitalize()
            opens = j.get("diningRoomHours").get(f"{d}Open")
            closes = j.get("diningRoomHours").get(f"{d}Close")
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.NEW_ZEALAND],
        max_search_distance_miles=500,
        expected_search_radius_miles=10,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

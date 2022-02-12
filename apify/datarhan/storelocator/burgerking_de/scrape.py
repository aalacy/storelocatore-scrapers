from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://euc1-prod-bk.rbictg.com/graphql"
    domain = "burgerking.de"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "X-Session-Id": "f2f3c21d-133b-4a1f-ba3c-6b10a3d79fc6",
        "x-user-datetime": "2021-08-12T19:34:20+02:00",
        "x-lr-session-url": "https://app.logrocket.com/mj7uvx/ctg-prod/s/4-ee18101c-97b9-4253-8990-13f3eadeef8d/0/08c2d611-63b5-4908-a504-6e717841c1a7?t=1628789660079",
        "x-ui-language": "de",
        "x-ui-region": "DE",
    }

    for lat, lng in DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY], expected_search_radius_miles=20
    ):
        frm = [
            {
                "operationName": "GetRestaurants",
                "query": "query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasMobileOrdering\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  id\n  isDarkKitchen\n  isFavorite\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n",
                "variables": {
                    "input": {
                        "coordinates": {
                            "searchRadius": 25000,
                            "userLat": lat,
                            "userLng": lng,
                        },
                        "filter": "NEARBY",
                        "first": 200,
                        "status": None,
                    }
                },
            }
        ]

        data = session.post(start_url, headers=hdr, json=frm).json()
        all_locations = data[0]["data"]["restaurants"]["nodes"]

        for poi in all_locations:
            page_url = f'https://www.burgerking.de/store-locator/store/{poi["_id"]}'
            street_address = poi["physicalAddress"]["address1"]
            if poi["physicalAddress"]["address2"]:
                street_address += " " + poi["physicalAddress"]["address2"]

            hoo = []
            hoo_dict = {}
            for k, time in poi["diningRoomHours"].items():
                if "_" in k:
                    continue
                if "Close" in k:
                    day = k.replace("Close", "")
                    if hoo_dict.get(day):
                        hoo_dict[day]["closes"] = time
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["closes"] = time
                else:
                    day = k.replace("Open", "")
                    if hoo_dict.get(day):
                        hoo_dict[day]["opens"] = time
                    else:
                        hoo_dict[day] = {}
                        hoo_dict[day]["opens"] = time
            for day, time in hoo_dict.items():
                hoo.append(f'{day} {time["opens"]} - {time["closes"]}')
            hours_of_operation = " ".join(hoo)
            phone = poi["phoneNumber"]
            if str(phone) == "0":
                phone = SgRecord.MISSING

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["name"],
                street_address=street_address,
                city=poi["physicalAddress"]["city"],
                state=poi["physicalAddress"]["stateProvince"],
                zip_postal=poi["physicalAddress"]["postalCode"],
                country_code=poi["physicalAddress"]["country"],
                store_number=page_url.split("_")[-1],
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hours_of_operation,
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

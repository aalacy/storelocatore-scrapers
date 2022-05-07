from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
}

logger = SgLogSetup().get_logger("popeyes_com")


def fetch_data():
    url = "https://use1-prod-plk.rbictg.com/graphql"
    website = "popeyes.com"
    country = "US"
    typ = "<MISSING>"
    payload = [
        {
            "operationName": "GetRestaurants",
            "variables": {
                "input": {
                    "filter": "NEARBY",
                    "coordinates": {
                        "userLat": 60,
                        "userLng": -150,
                        "searchRadius": 1024000,
                    },
                    "first": 500,
                    "status": "OPEN",
                }
            },
            "query": "query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasMobileOrdering\n  hasLateNightMenu\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  hasLoyalty\n  id\n  isDarkKitchen\n  isFavorite\n  isHalal\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n",
        }
    ]
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        if '"storeId":"' in line:
            items = line.split('"storeId":"')
            for item in items:
                if '"stateProvince":"' in item:
                    store = item.split('"')[0]
                    add = (
                        item.split('"address1":"')[1].split('"')[0]
                        + " "
                        + item.split('"address2":"')[1].split('"')[0]
                    )
                    add = add.strip()
                    loc = (
                        "https://www.popeyes.com/store-locator/store/"
                        + item.split(',"id":"')[1].split('"')[0]
                    )
                    state = item.split('"stateProvinceShort":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    phone = item.split('"phoneNumber":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    lat = item.split('latitude":')[1].split(",")[0]
                    lng = item.split('longitude":')[1].split(",")[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    name = name.replace("&amp;", "&")
                    if "," in name:
                        name = name.split(",")[0].strip()
                    add = add.replace("&amp;", "&")
                    hrs = item.split('"diningRoomHours":')[1].split('"__typename"')[0]
                    try:
                        hours = (
                            "Sunday: "
                            + hrs.split('"sunOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"sunClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = "Sunday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Monday: "
                            + hrs.split('"monOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"monClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Monday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Tuesday: "
                            + hrs.split('"tueOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"tueClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Tuesday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Wednesday: "
                            + hrs.split('"wedOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"wedClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Wednesday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Thursday: "
                            + hrs.split('"thrOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"thrClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Thursday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Friday: "
                            + hrs.split('"friOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"friClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Friday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Saturday: "
                            + hrs.split('"satOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"satClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Saturday: Closed"
                    if "&" in store:
                        store = store.split("&")[0]
                    if "?" in store:
                        store = store.split("?")[0]
                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )
    payload = [
        {
            "operationName": "GetRestaurants",
            "variables": {
                "input": {
                    "filter": "NEARBY",
                    "coordinates": {
                        "userLat": 20,
                        "userLng": -160,
                        "searchRadius": 1024000,
                    },
                    "first": 500,
                    "status": "OPEN",
                }
            },
            "query": "query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasMobileOrdering\n  hasLateNightMenu\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  hasLoyalty\n  id\n  isDarkKitchen\n  isFavorite\n  isHalal\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n",
        }
    ]
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        if '"storeId":"' in line:
            items = line.split('"storeId":"')
            for item in items:
                if '"stateProvince":"' in item:
                    store = item.split('"')[0]
                    add = (
                        item.split('"address1":"')[1].split('"')[0]
                        + " "
                        + item.split('"address2":"')[1].split('"')[0]
                    )
                    add = add.strip()
                    loc = (
                        "https://www.popeyes.com/store-locator/store/"
                        + item.split(',"id":"')[1].split('"')[0]
                    )
                    state = item.split('"stateProvinceShort":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    phone = item.split('"phoneNumber":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    lat = item.split('latitude":')[1].split(",")[0]
                    lng = item.split('longitude":')[1].split(",")[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    name = name.replace("&amp;", "&")
                    if "," in name:
                        name = name.split(",")[0].strip()
                    add = add.replace("&amp;", "&")
                    hrs = item.split('"diningRoomHours":')[1].split('"__typename"')[0]
                    try:
                        hours = (
                            "Sunday: "
                            + hrs.split('"sunOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"sunClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = "Sunday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Monday: "
                            + hrs.split('"monOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"monClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Monday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Tuesday: "
                            + hrs.split('"tueOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"tueClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Tuesday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Wednesday: "
                            + hrs.split('"wedOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"wedClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Wednesday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Thursday: "
                            + hrs.split('"thrOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"thrClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Thursday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Friday: "
                            + hrs.split('"friOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"friClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Friday: Closed"
                    try:
                        hours = (
                            hours
                            + "; Saturday: "
                            + hrs.split('"satOpen":"')[1].split(':00"')[0]
                            + "-"
                            + hrs.split('"satClose":"')[1].split(':00"')[0]
                        )
                    except:
                        hours = hours + "; Saturday: Closed"
                    if "&" in store:
                        store = store.split("&")[0]
                    if "?" in store:
                        store = store.split("?")[0]
                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )

    for x in range(-130, -60, 3):
        for y in range(20, 50, 3):
            logger.info(str(y) + " - " + str(x))
            payload = [
                {
                    "operationName": "GetRestaurants",
                    "variables": {
                        "input": {
                            "filter": "NEARBY",
                            "coordinates": {
                                "userLat": y,
                                "userLng": x,
                                "searchRadius": 512000,
                            },
                            "first": 500,
                            "status": "OPEN",
                        }
                    },
                    "query": "query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasMobileOrdering\n  hasLateNightMenu\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  hasLoyalty\n  id\n  isDarkKitchen\n  isFavorite\n  isHalal\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n",
                }
            ]

            r = session.post(url, headers=headers, data=json.dumps(payload))
            for line in r.iter_lines():
                if '"storeId":"' in line:
                    items = line.split('"storeId":"')
                    for item in items:
                        if '"stateProvince":"' in item:
                            store = item.split('"')[0]
                            add = (
                                item.split('"address1":"')[1].split('"')[0]
                                + " "
                                + item.split('"address2":"')[1].split('"')[0]
                            )
                            add = add.strip()
                            loc = (
                                "https://www.popeyes.com/store-locator/store/"
                                + item.split(',"id":"')[1].split('"')[0]
                            )
                            state = item.split('"stateProvinceShort":"')[1].split('"')[
                                0
                            ]
                            city = item.split('"city":"')[1].split('"')[0]
                            phone = item.split('"phoneNumber":"')[1].split('"')[0]
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            lat = item.split('latitude":')[1].split(",")[0]
                            lng = item.split('longitude":')[1].split(",")[0]
                            name = item.split('"name":"')[1].split('"')[0]
                            name = name.replace("&amp;", "&")
                            if "," in name:
                                name = name.split(",")[0].strip()
                            add = add.replace("&amp;", "&")
                            hrs = item.split('"diningRoomHours":')[1].split(
                                '"__typename"'
                            )[0]
                            try:
                                hours = (
                                    "Sunday: "
                                    + hrs.split('"sunOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"sunClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = "Sunday: Closed"
                            try:
                                hours = (
                                    hours
                                    + "; Monday: "
                                    + hrs.split('"monOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"monClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = hours + "; Monday: Closed"
                            try:
                                hours = (
                                    hours
                                    + "; Tuesday: "
                                    + hrs.split('"tueOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"tueClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = hours + "; Tuesday: Closed"
                            try:
                                hours = (
                                    hours
                                    + "; Wednesday: "
                                    + hrs.split('"wedOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"wedClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = hours + "; Wednesday: Closed"
                            try:
                                hours = (
                                    hours
                                    + "; Thursday: "
                                    + hrs.split('"thrOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"thrClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = hours + "; Thursday: Closed"
                            try:
                                hours = (
                                    hours
                                    + "; Friday: "
                                    + hrs.split('"friOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"friClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = hours + "; Friday: Closed"
                            try:
                                hours = (
                                    hours
                                    + "; Saturday: "
                                    + hrs.split('"satOpen":"')[1].split(':00"')[0]
                                    + "-"
                                    + hrs.split('"satClose":"')[1].split(':00"')[0]
                                )
                            except:
                                hours = hours + "; Saturday: Closed"
                            if "&" in store:
                                store = store.split("&")[0]
                            if "?" in store:
                                store = store.split("?")[0]
                            yield SgRecord(
                                locator_domain=website,
                                page_url=loc,
                                location_name=name,
                                street_address=add,
                                city=city,
                                state=state,
                                zip_postal=zc,
                                country_code=country,
                                phone=phone,
                                location_type=typ,
                                store_number=store,
                                latitude=lat,
                                longitude=lng,
                                hours_of_operation=hours,
                            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("dickeys_com")


def fetch_data(sgw: SgWriter):

    base_link = "https://orders-api.dickeys.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.dickeys.com/"
    found = []

    js = {
        "operationName": "getAllStates",
        "variables": {"first": 2147483647, "filter": [{"isOpened": {"eq": "true"}}]},
        "query": "query getAllStates($first: Int!, $filter: [LocationFilter]) {\n  viewer {\n    id\n    locationConnection(\n      first: $first\n      filter: $filter\n      sort: {address: {state: {label: ASC}}}\n    ) {\n      edges {\n        node {\n          id\n          address {\n            id\n            city\n            state {\n              id\n              stateId\n              label\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}",
    }

    locs = session.get(base_link, headers=headers, json=js).json()["data"]["viewer"][
        "locationConnection"
    ]["edges"]
    for loc in locs:
        loc_state = loc["node"]["address"]["state"]["label"]
        loc_city = loc["node"]["address"]["city"]
        city_state = loc_city + loc_state
        if city_state in found:
            continue
        found.append(city_state)
        if loc_state not in found:
            logger.info(loc_state)
            found.append(loc_state)
        true = "true"
        json = {
            "operationName": "getAllStoresInCity",
            "variables": {
                "first": 2147483647,
                "filter": [
                    {"isOpened": {"eq": true}},
                    {"address": {"state": {"label": {"eq": loc_state}}}},
                    {"address": {"city": {"eq": loc_city}}},
                ],
                "firstSubcategorySort": {"orderKey": "ASC"},
                "firstSubcategoryFilter": [
                    {"dontShowEmpty": {"eq": true}},
                    {"isAvailableOnline": {"eq": 1}},
                    {"category": {"categorytype": {"slug": {"eq": "everyday"}}}},
                ],
                "secondSubcategoryFilter": [
                    {"dontShowEmpty": {"eq": true}},
                    {"isAvailableOnline": {"eq": 1}},
                    {"category": {"categorytype": {"slug": {"eq": "catering"}}}},
                ],
                "thirdSubcategoryFilter": [
                    {"dontShowEmpty": {"eq": true}},
                    {"isAvailableOnline": {"eq": 1}},
                    {"category": {"categorytype": {"slug": {"eq": "holiday"}}}},
                ],
                "orderMenuLocationHandoffCategoryFilter": [
                    {
                        "active": {"eq": true},
                        "category": {"categorytype": {"slug": {"eq": "everyday"}}},
                        "handoff": {
                            "id": {
                                "in": [
                                    "SGFuZG9mZjoxOjk5OTktMTItMzEgMjM6NTk6NTkuMDAwMDAw",
                                    "SGFuZG9mZjoyOjk5OTktMTItMzEgMjM6NTk6NTkuMDAwMDAw",
                                ]
                            }
                        },
                    }
                ],
                "cateringMenuLocationHandoffCategoryFilter": [
                    {
                        "active": {"eq": true},
                        "category": {"categorytype": {"slug": {"eq": "catering"}}},
                        "handoff": {
                            "id": {
                                "in": [
                                    "SGFuZG9mZjoyOjk5OTktMTItMzEgMjM6NTk6NTkuMDAwMDAw"
                                ]
                            }
                        },
                    }
                ],
                "holidayMenuLocationHandoffCategoryFilter": [
                    {
                        "active": {"eq": true},
                        "category": {"categorytype": {"slug": {"eq": "holiday"}}},
                        "handoff": {
                            "id": {
                                "in": [
                                    "SGFuZG9mZjoyOjk5OTktMTItMzEgMjM6NTk6NTkuMDAwMDAw"
                                ]
                            }
                        },
                    }
                ],
            },
            "query": "query getAllStoresInCity($first: Int!, $filter: [LocationFilter], $firstSubcategorySort: [SubcategorySort], $firstSubcategoryFilter: [SubcategoryFilter], $secondSubcategoryFilter: [SubcategoryFilter], $thirdSubcategoryFilter: [SubcategoryFilter], $orderMenuLocationHandoffCategoryFilter: [LocationHandoffCategoryFilter], $cateringMenuLocationHandoffCategoryFilter: [LocationHandoffCategoryFilter], $holidayMenuLocationHandoffCategoryFilter: [LocationHandoffCategoryFilter]) {\n  viewer {\n    id\n    ...ViewerData\n    locationConnection(\n      first: $first\n      filter: $filter\n      sort: {address: {city: DESC}}\n    ) {\n      edges {\n        node {\n          id\n          label\n          slug\n          menuId\n          storeNumber\n          active\n          locationPicture\n          phone {\n            id\n            phone\n            __typename\n          }\n          menu {\n            id\n            orderMenuFirstSubcategory: subcategoryConnection(\n              sort: $firstSubcategorySort\n              filter: $firstSubcategoryFilter\n            ) {\n              edges {\n                node {\n                  id\n                  slug\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            cateringFirstSubcategory: subcategoryConnection(\n              sort: $firstSubcategorySort\n              filter: $secondSubcategoryFilter\n            ) {\n              edges {\n                node {\n                  id\n                  slug\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            holidayFirstSubcategory: subcategoryConnection(\n              sort: $firstSubcategorySort\n              filter: $thirdSubcategoryFilter\n            ) {\n              edges {\n                node {\n                  id\n                  slug\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          orderMenuHandoffCheck: locationHandoffCategoryConnection(\n            filter: $orderMenuLocationHandoffCategoryFilter\n          ) {\n            edges {\n              node {\n                id\n                handoff {\n                  id\n                  label\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          cateringMenuHandoffCheck: locationHandoffCategoryConnection(\n            filter: $cateringMenuLocationHandoffCategoryFilter\n          ) {\n            edges {\n              node {\n                id\n                handoff {\n                  id\n                  label\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          holidayMenuHandoffCheck: locationHandoffCategoryConnection(\n            filter: $holidayMenuLocationHandoffCategoryFilter\n          ) {\n            edges {\n              node {\n                id\n                handoff {\n                  id\n                  label\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          address {\n            id\n            city\n            zip\n            address\n            longitude\n            latitude\n            state {\n              id\n              label\n              abbreviation\n              __typename\n            }\n            __typename\n          }\n          store {\n            id\n            storeSalesVendorList\n            __typename\n          }\n          locationExclusiveDeliveryAddressConnection {\n            totalCount\n            edges {\n              node {\n                id\n                address {\n                  id\n                  address\n                  zip\n                  city\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          locationWeekdayConnection(filter: {showHoliday: {eq: true}}) {\n            edges {\n              node {\n                id\n                opened\n                active\n                closed\n                locationHours {\n                  id\n                  opened\n                  active\n                  closed\n                  __typename\n                }\n                weekday {\n                  weekdayId\n                  id\n                  type\n                  label\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ViewerData on Viewer {\n  id\n  personId\n  firstName\n  email\n  __typename\n}",
        }

        stores = session.get(base_link, headers=headers, json=json).json()["data"][
            "viewer"
        ]["locationConnection"]["edges"]

        for i in stores:
            store = i["node"]
            street_address = store["address"]["address"]
            if street_address in found:
                continue
            city = store["address"]["city"]
            state = store["address"]["state"]["label"]
            zip_code = store["address"]["zip"]
            country_code = "US"
            store_number = store["storeNumber"]
            location_type = "<MISSING>"
            phone = store["phone"]["phone"]
            latitude = store["address"]["latitude"]
            longitude = store["address"]["longitude"]
            slug = store["slug"]
            if "wing-boss" in slug or "burger" in slug or "trailer-birds" in slug:
                continue
            found.append(street_address)
            location_name = city.title() + " - " + slug.replace("-", " ").title()
            link = "https://www.dickeys.com/locations/%s/%s/%s" % (state, city, slug)

            hours_of_operation = ""
            raw_hours = store["locationWeekdayConnection"]["edges"]
            for y in raw_hours:
                row = y["node"]
                if row["locationHours"][0]["active"]:
                    hours = (
                        row["locationHours"][0]["opened"]
                        + "-"
                        + row["locationHours"][0]["closed"]
                    )
                else:
                    hours = "Closed"
                day = row["weekday"]["label"]
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + hours
                ).strip()
            hours_of_operation = (
                hours_of_operation.split("Thanks")[0].split("Chris")[0].strip()
            )

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)

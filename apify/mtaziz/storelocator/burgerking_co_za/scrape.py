from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sglogging import SgLogSetup
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
logger = SgLogSetup().get_logger(logger_name="burgerking_co_za")
domain = "burgerking.co.za"
STORE_LOCATOR = "https://www.burgerking.co.za/store-locator"
logger.info(f"Store Locator: {STORE_LOCATOR}")

API_ENDPOINT_URL = "https://use1-prod-bk.rbictg.com/graphql"

# During maintenance this search can be used to search.
search_keywords = "Lagos Tavern, Rosina Road, Bellavista, Johannesburg, South Africa"
logger.info(f"Search Keywords: {search_keywords}")


latitude_za = -34.087223
longitude_za = 18.360556

# First 200 stores considered to be scraped.
# Status must be None so that it covers all the stores.
payload_dquoted_entire_country = [
    {
        "operationName": "GetRestaurants",
        "variables": {
            "input": {
                "filter": "NEARBY",
                "coordinates": {
                    "userLat": latitude_za,
                    "userLng": longitude_za,
                    "searchRadius": 1024000,
                },
                "first": 200,
                "status": None,
            }
        },
        "query": "query GetRestaurants($input: RestaurantsInput) {  restaurants(input: $input) {    pageInfo {      hasNextPage      endCursor      __typename    }    totalCount    nodes {      ...RestaurantNodeFragment      __typename    }    __typename  }}fragment RestaurantNodeFragment on RestaurantNode {  _id  storeId  isAvailable  posVendor  chaseMerchantId  curbsideHours {    ...OperatingHoursFragment    __typename  }  deliveryHours {    ...OperatingHoursFragment    __typename  }  diningRoomHours {    ...OperatingHoursFragment    __typename  }  distanceInMiles  drinkStationType  driveThruHours {    ...OperatingHoursFragment    __typename  }  driveThruLaneType  email  environment  franchiseGroupId  franchiseGroupName  frontCounterClosed  hasBreakfast  hasBurgersForBreakfast  hasCatering  hasCurbside  hasDelivery  hasDineIn  hasDriveThru  hasTableService  hasMobileOrdering  hasLateNightMenu  hasParking  hasPlayground  hasTakeOut  hasWifi  hasLoyalty  id  isDarkKitchen  isFavorite  isHalal  isRecent  latitude  longitude  mobileOrderingStatus  name  number  parkingType  phoneNumber  physicalAddress {    address1    address2    city    country    postalCode    stateProvince    stateProvinceShort    __typename  }  playgroundType  pos {    vendor    __typename  }  posRestaurantId  restaurantImage {    asset {      _id      metadata {        lqip        palette {          dominant {            background            foreground            __typename          }          __typename        }        __typename      }      __typename    }    crop {      top      bottom      left      right      __typename    }    hotspot {      height      width      x      y      __typename    }    __typename  }  restaurantPosData {    _id    __typename  }  status  vatNumber  __typename}fragment OperatingHoursFragment on OperatingHours {  friClose  friOpen  monClose  monOpen  satClose  satOpen  sunClose  sunOpen  thrClose  thrOpen  tueClose  tueOpen  wedClose  wedOpen  __typename}",
    }
]

logger.info(f"Payload: {payload_dquoted_entire_country}")


# Headers must be like below.
headers_special = {
    "authority": "use1-prod-bk.rbictg.com",
    "method": "POST",
    "path": "/graphql",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "x-ui-language": "en",
    "x-ui-platform": "web",
    "x-ui-region": "ZA",
}


def fetch_data():
    with SgRequests() as session_za:
        rpost_entire = session_za.post(
            API_ENDPOINT_URL,
            data=json.dumps(payload_dquoted_entire_country),
            headers=headers_special,
        )
        js_data = rpost_entire.json()

        all_locations = js_data[0]["data"]["restaurants"]["nodes"]
        for poi in all_locations:
            page_url = f'https://www.burgerking.co.za/store-locator/store/{poi["_id"]}'
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
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()

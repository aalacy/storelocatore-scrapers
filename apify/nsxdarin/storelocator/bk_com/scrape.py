from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import static_coordinate_list
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("bk_com")


session = SgRequests()
headers = {
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with SgWriter(
        deduper=SgRecordDeduper(
            record_id=RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in data:
            writer.write_row(rec)


def build_body(lat, lng):
    return {
        "operationName": "GetRestaurants",
        "variables": {
            "input": {
                "filter": "NEARBY",
                "coordinates": {
                    "userLat": float(lat),
                    "userLng": float(lng),
                    "searchRadius": 500000,
                },
                "first": 20000,
            }
        },
        "query": """query GetRestaurants($input: RestaurantsInput) {
            restaurants(input: $input) {
                pageInfo {
                    hasNextPage
                    endCursor
                    __typename
                    }
                    totalCount
                    nodes {
                    ...RestaurantNodeFragment
                    __typename
                    }
                    __typename
                }
            }

            fragment RestaurantNodeFragment on RestaurantNode {
                _id
                storeId
                diningRoomHours {
                    ...OperatingHoursFragment
                    __typename
                }
                franchiseGroupId
                franchiseGroupName
                latitude
                longitude
                name
                phoneNumber
                physicalAddress {
                    address1
                    address2
                    city
                    country
                    postalCode
                    stateProvince
                    stateProvinceShort
                    __typename
                }
            }

            fragment OperatingHoursFragment on OperatingHours {
                friClose
                friOpen
                monClose
                monOpen
                satClose
                satOpen
                sunClose
                sunOpen
                thrClose
                thrOpen
                tueClose
                tueOpen
                wedClose
                wedOpen
                __typename
            }
        """,
    }


def fetch_locations(lat, lng, session, retry=0):
    try:
        result = session.post(
            "https://use1-prod-bk.rbictg.com/graphql",
            headers=headers,
            json=build_body(lat, lng),
        ).json()

        return result["data"]["restaurants"]["nodes"]
    except Exception as e:
        if retry < 3:
            return fetch_locations(lat, lng, session, retry + 1)

        raise e


def fetch_data():
    search = static_coordinate_list(100)
    session = SgRequests()
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(fetch_locations, lat, lng, session) for lat, lng in search
        ]
        for future in as_completed(futures):
            locations = future.result()
            for location in locations:
                locator_domain = "bk.com"
                location_type = location["franchiseGroupId"]
                location_name = location["name"]
                store_number = location["storeId"]
                page_url = f'https://www.bk.com/store-locator/store/{location["_id"]}'

                phone = location["phoneNumber"]

                physical = location["physicalAddress"]

                street_address = physical["address1"]
                if physical["address2"]:
                    street_address += f', {physical["address2"]}'

                city = physical["city"]
                state = physical["stateProvinceShort"]
                postal = physical["postalCode"]
                country_code = physical["country"]

                latitude = location["latitude"]
                longitude = location["longitude"]

                hours_of_operation = []
                days = ["mon", "tue", "wed", "thr", "fri", "sat", "sun"]
                for day in days:
                    opens = location["diningRoomHours"][f"{day}Open"]
                    closes = location["diningRoomHours"][f"{day}Close"]

                    hours_of_operation.append(f"{day}: {opens}-{closes}")

                hours_of_operation = ",".join(hours_of_operation)

                yield SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_type=location_type,
                    location_name=location_name,
                    store_number=store_number,
                    phone=phone,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

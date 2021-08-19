import csv
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
import phonenumbers
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("dillons_com")


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


@retry(stop=stop_after_attempt(7))
def query_zip(zip_code):
    session = SgRequests()
    headers = {
        "User-Agent": "PostmanRuntime/7.19.0",
        "content-type": "application/json;charset=UTF-8",
    }
    data = (
        r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'
        + str(zip_code)
        + '","filters":[]},"operationName":"storeSearch"}'
    )
    r = session.post(
        "https://www.dillons.com/stores/api/graphql", headers=headers, data=data
    )
    return r.json()["data"]["storeSearch"]


def fetch_data():
    locator_domain = "https://www.dillons.com/"
    addresses = set()
    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=100,
    )
    for zip_code in zip_codes:
        datas = query_zip(zip_code)
        result_coords = []
        if datas is not None:
            for key in datas["stores"]:
                location_name = key["vanityName"]
                street_address = key["address"]["addressLine1"].capitalize()
                city = key["address"]["city"].capitalize()
                state = key["address"]["stateCode"]
                zipp = key["address"]["zip"]
                country_code = key["address"]["countryCode"]
                store_number = key["storeNumber"]
                if key["phoneNumber"]:
                    phone = phonenumbers.format_number(
                        phonenumbers.parse(str(key["phoneNumber"]), "US"),
                        phonenumbers.PhoneNumberFormat.NATIONAL,
                    )
                else:
                    phone = "<MISSING>"
                if key["banner"]:
                    location_type = key["banner"]
                else:
                    location_type = "store"
                latitude = key["latitude"]
                longitude = key["longitude"]
                zip_codes.found_location_at(latitude, longitude)
                hours_of_operation = ""
                if key["ungroupedFormattedHours"]:
                    for hr in key["ungroupedFormattedHours"]:
                        hours_of_operation += (
                            hr["displayName"] + ": " + hr["displayHours"] + ", "
                        )
                else:
                    hours_of_operation = "<INACCESSIBLE>"
                page_url = (
                    "https://www.dillons.com/stores/details/"
                    + str(key["divisionNumber"])
                    + "/"
                    + str(store_number)
                )

                store = []
                store.append(locator_domain if locator_domain else "<MISSING>")
                store.append(location_name if location_name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append(location_type if location_type else "<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                store.append(page_url)
                if store[2] in addresses:
                    continue
                addresses.add(store[2])
                yield store
        if datas is not None:
            if "fuel" in datas:
                for key1 in datas["fuel"]:
                    location_name = key1["vanityName"]
                    street_address = key1["address"]["addressLine1"].capitalize()
                    city = key1["address"]["city"].capitalize()
                    state = key1["address"]["stateCode"]
                    zipp = key1["address"]["zip"]
                    country_code = key1["address"]["countryCode"]
                    store_number = key1["storeNumber"]
                    phone = key1["phoneNumber"]
                    if key["banner"]:
                        location_type = key["banner"]
                    else:
                        location_type = "fuel"
                    latitude = key1["latitude"]
                    longitude = key1["longitude"]
                    result_coords.append((latitude, longitude))
                    hours_of_operation = ""
                    if key1["ungroupedFormattedHours"]:
                        for hr in key1["ungroupedFormattedHours"]:
                            hours_of_operation += (
                                hr["displayName"] + ": " + hr["displayHours"] + ", "
                            )
                    else:
                        hours_of_operation = "<MISSING>"
                    page_url = (
                        "https://www.dillons.com/stores/details/"
                        + str(key1["divisionNumber"])
                        + "/"
                        + str(store_number)
                    )
                    store = []
                    store.append(locator_domain if locator_domain else "<MISSING>")
                    store.append(location_name if location_name else "<MISSING>")
                    store.append(street_address if street_address else "<MISSING>")
                    store.append(city if city else "<MISSING>")
                    store.append(state if state else "<MISSING>")
                    store.append(zipp if zipp else "<MISSING>")
                    store.append(country_code if country_code else "<MISSING>")
                    store.append(store_number if store_number else "<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type if location_type else "<MISSING>")
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(
                        hours_of_operation if hours_of_operation else "<MISSING>"
                    )
                    store.append(page_url)
                    if store[2] in addresses:
                        continue
                    addresses.add(store[2])
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

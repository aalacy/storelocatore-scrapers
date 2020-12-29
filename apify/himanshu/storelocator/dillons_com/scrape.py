import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("dillons_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
    }
    addresses = []
    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=100,
    )
    for zip_code in zip_codes:
        result_coords = []
        r_data = (
            r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'
            + zip_code
            + r'","filters":[]},"operationName":"storeSearch"}'
        )
        r = session.post(
            "https://www.dillons.com/stores/api/graphql", headers=headers, data=r_data
        )
        try:
            data = r.json()["data"]["storeSearch"]
        except:
            continue
        for loc_tpye in data:
            if type(data[loc_tpye]) != list:
                continue
            for store_data in data[loc_tpye]:
                lat = store_data["latitude"]
                lng = store_data["longitude"]
                result_coords.append((lat, lng))
                store = []
                store.append("https://www.dillons.com")
                store.append(store_data["vanityName"])
                address = store_data["address"]
                store.append(
                    address["addressLine1"] + " " + address["addressLine2"]
                    if address["addressLine2"] is not None
                    else address["addressLine1"]
                )
                store.append(address["city"])
                store.append(address["stateCode"])
                store.append(address["zip"])
                store.append(address["countryCode"])
                store.append(
                    str(store_data["divisionNumber"])
                    + "-"
                    + str(store_data["storeNumber"])
                )
                store.append(
                    store_data["phoneNumber"]
                    if "phoneNumber" in store_data
                    and store_data["phoneNumber"] != ""
                    and store_data["phoneNumber"] is not None
                    else "<MISSING>"
                )
                store.append("dillons " + loc_tpye)
                store.append(lat)
                store.append(lng)
                hours = ""
                store_hours = store_data["ungroupedFormattedHours"]
                for hour_detail in store_hours:
                    hours = (
                        hours
                        + " "
                        + hour_detail["displayName"]
                        + " "
                        + hour_detail["displayHours"]
                    )
                store.append(hours if hours != "" else "<MISSING>")
                store.append("https://www.dillons.com/stores/")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

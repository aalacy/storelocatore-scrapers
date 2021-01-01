import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgselenium import SgChrome

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="picknsave.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    api_link = "https://www.picknsave.com/stores/api/graphql"

    driver = SgChrome().chrome()

    driver.get(api_link)

    cookies = driver.get_cookies()
    cookie = ""
    for cook in cookies:
        cookie = cookie + cook["name"] + "=" + cook["value"] + "; "
    cookie = cookie.strip()[:-1]

    session = SgRequests()

    data = []
    found_poi = []

    max_results = 50
    max_distance = 100

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Searching items..Appr. 10mins..")

    for zipcode in search:
        json = {
            "query": "\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n",
            "variables": {"searchText": zipcode, "filters": []},
            "operationName": "storeSearch",
        }

        headers = {
            "authority": "www.picknsave.com",
            "method": "POST",
            "path": "/stores/api/graphql",
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "content-length": "1042",
            "content-type": "application/json;charset=UTF-8",
            "cookie": cookie,
            "origin": "https://www.picknsave.com",
            "referer": "https://www.picknsave.com/stores/search?searchText=" + zipcode,
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
            "x-dtpc": "7$174174090_580h27vHMNHMKRUIIPAAGUKSOTMSHSBHPHRRMGO-0e7",
            "x-dtreferer": "https://www.picknsave.com/stores/search",
        }

        store_data = session.post(api_link, headers=headers, json=json).json()["data"][
            "storeSearch"
        ]["stores"]
        fuel_data = session.post(api_link, headers=headers, json=json).json()["data"][
            "storeSearch"
        ]["fuel"]

        locator_domain = "picknsave.com"

        for store in store_data:
            store_number = store["storeNumber"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)

            link = "https://www.picknsave.com/stores/details/%s/%s" % (
                store["divisionNumber"],
                store_number,
            )
            location_name = store["vanityName"]
            try:
                street_address = (
                    store["address"]["addressLine1"]
                    + " "
                    + store["address"]["addressLine2"]
                ).strip()
            except:
                street_address = store["address"]["addressLine1"].strip()
            city = store["address"]["city"]
            state = store["address"]["stateCode"]
            zip_code = store["address"]["zip"]
            country_code = "US"
            location_type = "Store"

            phone = store["phoneNumber"]
            if not phone:
                phone = "<MISSING>"

            hours_of_operation = ""
            raw_hours = store["ungroupedFormattedHours"]
            for hours in raw_hours:
                day = hours["displayName"]
                opens = day + " " + hours["displayHours"]
                hours_of_operation = (hours_of_operation + " " + opens).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.mark_found([latitude, longitude])

            data.append(
                [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

        for store in fuel_data:
            store_number = store["storeNumber"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)

            link = "https://www.picknsave.com/stores/details/%s/%s" % (
                store["divisionNumber"],
                store_number,
            )
            location_name = store["vanityName"]
            try:
                street_address = (
                    store["address"]["addressLine1"]
                    + " "
                    + store["address"]["addressLine2"]
                ).strip()
            except:
                street_address = store["address"]["addressLine1"].strip()
            city = store["address"]["city"]
            state = store["address"]["stateCode"]
            zip_code = store["address"]["zip"]
            country_code = "US"
            location_type = "Fuel"

            phone = store["phoneNumber"]
            if not phone:
                phone = "<MISSING>"

            hours_of_operation = ""
            raw_hours = store["ungroupedFormattedHours"]
            for hours in raw_hours:
                day = hours["displayName"]
                opens = day + " " + hours["displayHours"]
                hours_of_operation = (hours_of_operation + " " + opens).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]
            search.mark_found([latitude, longitude])

            data.append(
                [
                    locator_domain,
                    link,
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country_code,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

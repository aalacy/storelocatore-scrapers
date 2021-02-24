import csv

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

base_url = "https://www.bigotires.com"


def validate(item):
    if type(item) == list:
        item = " ".join(item)
    return item.strip()


def get_value(item):
    if item is None:
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != "":
            rets.append(item)
    return rets


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    output_list = []
    store_ids = []

    headers = {
        "authority": "www.bigotires.com",
        "method": "POST",
        "path": "/restApi/dp/v1/store/storesByAddress",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-length": "41",
        "content-type": "application/json;charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "x-requested-by": "123",
        "x-requested-with": "XMLHttpRequest",
    }

    session = SgRequests()
    url = "https://www.bigotires.com/restApi/dp/v1/store/storesByAddress"

    max_distance = 200

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
    )

    for postcode in search:
        # query the store locator using zip

        data = {"address": postcode, "distanceInMiles": max_distance}

        source = session.post(url, headers=headers, json=data).json()

        if "storesType" not in list(source.keys()):
            continue

        store_list = source["storesType"]

        if "stores" not in list(store_list.keys()):
            continue

        store_list = store_list["stores"]
        for store in store_list:
            store_id = validate(store["storeId"])
            if store_id in store_ids:
                continue
            store_ids.append(store_id)
            store_hours = store["workingHours"]
            hours = ""
            for x in store_hours:
                if validate(x["openingHour"]) == "Closed ":
                    hours += x["day"] + " " + x["openingHour"] + " "
                else:
                    hours += (
                        x["day"] + " " + x["openingHour"] + "-" + x["closingHour"] + " "
                    )
            store_closed_hours = store["storeClosedHours"]
            for x in store_closed_hours:
                hours += validate(x["date"] + ": " + x["workingHours"] + " ")
            hours = hours.replace("Closed-Closed", "Closed").strip()
            output = []
            output.append(base_url)  # url
            output.append(base_url + store["storeDetailsUrl"])
            output.append(validate(store["address"]["address1"]))  # location name
            output.append(validate(store["address"]["address1"]))  # address
            output.append(validate(store["address"]["city"]))  # city
            output.append(validate(store["address"]["state"]))  # state
            output.append(validate(store["address"]["zipcode"]))  # zipcode
            output.append("US")  # country code
            output.append(store_id)  # store_number
            output.append(validate(store["phoneNumbers"][0]))  # phone
            output.append("<MISSING>")  # location type
            latitude = store["mapCenter"]["latitude"]
            longitude = store["mapCenter"]["longitude"]
            output.append(latitude)  # latitude
            output.append(longitude)  # longitude
            search.found_location_at(latitude, longitude)

            output.append(get_value(hours))  # opening hours
            output_list.append(output)

    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

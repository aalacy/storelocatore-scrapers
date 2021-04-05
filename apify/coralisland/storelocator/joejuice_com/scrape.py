import csv
import json

from sgrequests import SgRequests

base_url = "https://www.joejuice.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


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


def fetch_data():
    output_list = []
    url = "https://joepay-api.joejuice.com/me/stores"
    session = SgRequests()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        if "America" in get_value(store["timezone"]):
            country = "United States"
        elif "London" in get_value(store["timezone"]):
            country = "United Kingdom"
        else:
            continue
        output.append(base_url)  # url
        output.append(get_value(store["name"]))  # location name
        zip_code = "<MISSING>"
        street_address = get_value(store["address"])
        if "B91 3RA" in store["address"]:
            zip_code = "B91 3RA"
            street_address = street_address.replace("B91 3RA", "").strip()
        output.append(street_address)  # address
        city = store["name"].split("[")[1].replace("]", "").strip()
        if country == "United States":
            if (
                "San " not in city
                and "Beach" not in city
                and "Paul" not in city
                and "Pitt" not in city
                and "Seattle" not in city
                and "Brentwood" not in city
                and "Beverly" not in city
                and "Hollywood" not in city
                and "Glendale" not in city
                and "Palo" not in city
                and "Miami" not in city
                and "Corte" not in city
            ):
                city = "<MISSING>"
        output.append(city)  # city
        output.append("<MISSING>")  # state
        output.append(zip_code)  # zipcode
        output.append(country)  # country code
        output.append(get_value(store["externalId"]))  # store_number
        output.append("<MISSING>")  # phone
        output.append(
            "Date Active " + store["availableAt"].split("T")[0]
        )  # location type
        output.append(get_value(store["latitude"]))  # latitude
        output.append(get_value(store["longitude"]))  # longitude
        store_hours = []

        raw_hours = store["storeBusinessHours"]
        if raw_hours:
            for row in raw_hours:
                day = (
                    str(row["day"])
                    .replace("0", "Mon")
                    .replace("1", "Tue")
                    .replace("2", "Wed")
                    .replace("3", "Thu")
                    .replace("4", "Fri")
                    .replace("5", "Sat")
                    .replace("6", "Sun")
                )
                if row["closed"]:
                    hour = "closed"
                else:
                    hour = row["openTime"] + "-" + row["closeTime"]
                store_hours.append(day + " " + hour)
        else:
            store_hours = "Store is closed"
        output.append(get_value(store_hours))  # opening hours
        output.append("https://www.joejuice.com/stores")
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

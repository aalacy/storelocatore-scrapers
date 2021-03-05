import csv
import json

from sgrequests import SgRequests

base_url = "http://cardenasmarkets.com"


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
    url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=PVNACVHMHURQFNUF&center=37.3053,-113.6706&multi_account=false&pageSize=500"
    session = SgRequests()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        page_url = "https://locations.cardenasmarkets.com" + get_value(store["llp_url"])
        store = store["store_info"]
        output.append(base_url)  # url
        output.append(page_url)  # page url
        output.append(get_value(store["name"]))  # location name
        output.append(get_value(store["address"]))  # address
        output.append(get_value(store["locality"]))  # city
        output.append(get_value(store["region"]))  # state
        output.append(get_value(store["postcode"]))  # zipcode
        output.append(get_value(store["country"]))  # country code
        output.append(get_value(store["corporate_id"]))  # store_number
        output.append(get_value(store["phone"]))  # phone
        output.append("<MISSING>")  # location type
        output.append(get_value(store["latitude"]))  # latitude
        output.append(get_value(store["longitude"]))  # longitude
        days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        store_hours = []
        hours = eliminate_space(validate(store["store_hours"]).split(";"))
        for hour in hours:
            hour = hour.split(",")
            temp = (
                days_of_week[int(hour[0]) - 1]
                + " "
                + hour[1][:2]
                + ":"
                + hour[1][2:]
                + "-"
                + hour[2][:2]
                + ":"
                + hour[2][2:]
            )
            store_hours.append(temp)
        output.append(get_value(store_hours))  # opening hours
        output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

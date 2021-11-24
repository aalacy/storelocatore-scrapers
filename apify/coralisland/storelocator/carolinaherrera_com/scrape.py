import csv
import json

from sgrequests import SgRequests

base_url = "https://www.carolinaherrera.com"


def validate(item):
    if item is None:
        item = ""
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = " ".join(item)
    return item.replace("\u2013", "-").strip()


def get_value(item):
    if item is None or item == "NULL":
        item = "<MISSING>"
    item = validate(item)
    if item == "":
        item = "<MISSING>"
    return item


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
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
    history = []
    output_list = []
    url = (
        "https://carolinaherreraboutiques.com/api/stores?lat=40.7127753&lng=-74.0059728"
    )
    session = SgRequests()
    page_source = json.loads(session.get(url).text)
    total_pages = int(page_source["data"]["pager"]["total_pages"]) + 1

    for idx in range(0, total_pages):
        url = (
            "https://carolinaherreraboutiques.com/api/stores?lat=40.7127753&lng=-74.0059728&page="
            + str(idx)
        )
        request = session.get(url)
        store_list = json.loads(request.text)["data"]["rows"]
        for store in store_list:
            output = []
            country = get_value(store["country_code"])
            store_id = get_value(store["store_id"])
            if store_id not in history:
                history.append(store_id)
                page_url = "https://store-locator.carolinaherrera.com/en/" + validate(
                    store["slug"]
                )
                output.append(base_url)
                output.append(page_url)
                output.append(get_value(store["store_name"]))
                output.append(get_value(store["address_1"]))
                output.append(get_value(store["city"]))
                output.append(get_value(store["state"]))
                output.append(get_value(store["postal_code"]))
                output.append(country)
                output.append(store_id)
                output.append(get_value(store["phone_number"]))
                output.append(get_value(store["store_type"]))
                output.append(get_value(store["latitude"]))
                output.append(get_value(store["longitude"]))
                store_hours = []
                for hour in store["store_timings"]:
                    if validate(hour["start_day"]) != validate(hour["end_day"]):
                        temp = (
                            validate(hour["start_day"])
                            + " - "
                            + validate(hour["end_day"])
                            + " "
                            + validate(hour["from_time"])
                            + " - "
                            + validate(hour["to_time"])
                        )
                    else:
                        temp = (
                            validate(hour["start_day"])
                            + " "
                            + validate(hour["from_time"])
                            + " - "
                            + validate(hour["to_time"])
                        )
                    store_hours.append(temp)
                output.append(get_value(store_hours))
                if get_value(store["city"]) != "Sao Paolo":
                    output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

import csv
from sgrequests import SgRequests
import json
from datetime import datetime


base_url = "https://www.nationalcar.com"


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
    urls = [
        "https://prd.location.enterprise.com/enterprise-sls/search/location/national/web/country/US?locale=en_US&cor=US",
        "https://prd.location.enterprise.com/enterprise-sls/search/location/national/web/country/CA?locale=en_US&cor=US",
        "https://prd.location.enterprise.com/enterprise-sls/search/location/national/web/country/GB?locale=en_US&cor=US",
    ]

    session = SgRequests()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    for url in urls:
        request = session.get(url, headers=headers)
        store_list = json.loads(request.text)
        for store in store_list:
            output = []
            output.append(base_url)  # url
            output.append(get_value(store["locationNameTranslation"]))  # location name
            output.append(get_value(store["addressLines"]))  # address
            output.append(get_value(store["city"]))  # city
            try:
                output.append(get_value(store["state"]))  # state
            except:
                output.append("<MISSING>")
            output.append(get_value(store["postalCode"]))  # zipcode
            output.append(get_value(store["countryCode"]))  # country code
            output.append("<MISSING>")  # store_number
            output.append(get_value(store["phoneNumber"]))  # phone
            output.append(get_value(store["locationType"]))  # location type
            output.append(get_value(store["latitude"]))  # latitude
            output.append(get_value(store["longitude"]))  # longitude
            today = datetime.today().strftime("%Y-%m-%d")
            data = session.get(
                "https://prd.location.enterprise.com/enterprise-sls/search/location/national/web/hours/"
                + store["peopleSoftId"]
                + "?from="
                + today
                + "&to="
                + today
                + "&locale=en_US&cor=US"
            ).text
            data = json.loads(data)["data"][today]["STANDARD"]["hours"]
            hours = []
            for dat in data:
                hours.append(dat["open"] + "-" + dat["close"])
            store_hours = []
            if len(hours) != 0:
                day_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                for day in day_of_week:
                    store_hours.append(day + " " + validate(hours))
            output.append(get_value(store_hours))  # opening hours
            output_list.append(output)
    return output_list


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

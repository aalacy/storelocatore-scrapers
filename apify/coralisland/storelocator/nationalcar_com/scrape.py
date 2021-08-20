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
            lname = get_value(store["locationNameTranslation"])
            branch = get_value(store["groupBranchNumber"])
            lurl = ""
            try:
                lurlus = (
                    "https://www.nationalcar.com/en/car-rental/locations/us/"
                    + get_value(store["state"]).lower()
                    + "/"
                    + lname.lower().replace(" ", "-").replace(".", "").replace("'", "")
                    + "-"
                    + branch
                    + ".html"
                )
            except:
                lurlus = "<MISSING>"
            try:
                lurlca = (
                    "https://www.nationalcar.com/en/car-rental/locations/ca/"
                    + get_value(store["state"]).lower()
                    + "/"
                    + lname.lower().replace(" ", "-").replace(".", "").replace("'", "")
                    + "-"
                    + branch
                    + ".html"
                )
            except:
                lurlca = "<MISSING>"
            lurlgb = (
                "https://www.nationalcar.com/en/car-rental/locations/gb/"
                + lname.lower().replace(" ", "-").replace(".", "").replace("'", "")
                + "-"
                + branch
                + ".html"
            )
            if "/US" in url:
                lurl = lurlus
            if "/CA" in url:
                lurl = lurlca
            if "/GB" in url:
                lurl = lurlgb
            output.append(lurl)
            output.append(get_value(store["locationNameTranslation"]))  # location name
            addinfo = get_value(store["addressLines"])
            if "1978) Ltd" in addinfo:
                addinfo = addinfo.split(") Ltd")[1].strip()
            if "Enterprise Rent A Car" in addinfo:
                addinfo = addinfo.split("Rent A Car")[1].strip()
            addinfo = addinfo.replace("Williamsport Regional Airport ", "")
            addinfo = addinfo.replace("Ronald Reagan Wash Natl Airprt ", "")
            addinfo = addinfo.replace("Luis Munoz Marin Intl Airport ", "")
            output.append(addinfo)  # address
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

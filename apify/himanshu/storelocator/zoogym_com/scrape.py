import csv
from sgrequests import SgRequests
import json

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

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
    base_url = "https://www.zoogym.com/wp-admin/admin-ajax.php?action=store_search&lat=26.101509&lng=-80.26195999999999&max_results=25&search_radius=50&autoload=1"
    r = session.get(base_url, headers=headers)
    soup = json.loads(r.text)
    store_name = []
    store_detail = []
    return_main_object = []
    for i in soup:
        tem_var = []
        street_address = i["address"]
        city = i["city"]
        state = i["state"]
        zipcode = i["zip"]
        country_code = "US"
        phone = i["phone"]
        if len(phone) < 1:
            phone = "<MISSING>"
        location_type = "zoogym"
        latitude = i["lat"]
        longitude = i["lng"]
        hours_of_operation = "<MISSING>"
        name = (
            i["store"]
            .replace("<br>", " ")
            .replace("<br />", "")
            .replace("(Visit Our Site)", "")
            .replace("</a>", "")
        )
        store_name.append(name.rstrip())

        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append(country_code)
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append(location_type)
        tem_var.append(latitude)
        tem_var.append(longitude)
        tem_var.append(hours_of_operation)
        store_detail.append(tem_var)
    return_main_object = []
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.zoogym.com")
        store.append("https://zoogym.com/locations-2/")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

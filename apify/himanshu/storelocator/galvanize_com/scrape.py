import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("galvanize_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    return_main_object = []
    address = []
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
    }

    locator_domain = "https://www.galvanize.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    r = session.get("https://www.galvanize.com", headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    li = soup.find("li", {"data-tag": "Campuses"}).find_all("a")
    for i in li:
        if "/campuses/remote" in i["href"] or "/campuses/san-jose" in i["href"]:
            continue
        r_loc = session.get(locator_domain + i["href"], headers=headers)
        soup = BeautifulSoup(r_loc.text, "html5lib")
        loc = soup.find("textarea", {"id": "state"}).text
        script_text = loc.split(',"location":')[-1].split("}")[0] + "}"
        try:
            json_data = eval(script_text)
        except:
            pass
        latitude = json_data["lat"]
        longitude = json_data["lon"]
        zipp = json_data["zip"].replace("90045", "90401")
        city = json_data["city"]
        location_name = json_data["name"]
        phone = json_data["phone"]
        state = json_data["state"]
        street_address = json_data["address"].replace(", Santa Monica, CA 90401", "")
        page_url = locator_domain + i["href"]

        store = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zipp,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
            page_url,
        ]
        store = ["<MISSING>" if x == "" or x == "Blank" else x for x in store]
        if store[2] in address:
            address.append(store[2])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

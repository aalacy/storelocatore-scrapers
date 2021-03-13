import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

session = SgRequests()


def write_output(data):
    with open("data.csv", "w") as output_file:
        writer = csv.writer(output_file, delimiter=",")
        # header
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
        # body
        for row in data or []:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    get_url = "https://www.larsensrestaurants.com/locations-and-menus"
    base_url = "https://larsensrestaurants.com/"
    r1 = session.get(base_url, headers=headers)
    soup1 = BeautifulSoup(r1.text, "lxml")
    hours_list = []
    l_name = []
    for h in soup1.findAll("div", class_="hours"):
        hours = " ".join(list(h.stripped_strings)).split("Join us")[0]
        if "Happy Hour Daily*" in hours:
            hours = hours.split("Happy Hour Daily*")[0]
        hours_list.append(hours)
        l_name.append(h.parent.h4.text.strip())

    r = session.get(get_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("script", {"class": "js-react-on-rails-component"}).contents[0]
    js = json.loads(main)

    obj = js["preloadQueries"][0]["data"]["restaurant"]["homePage"]["sections"][-1][
        "locations"
    ]
    for index, i in enumerate(obj):
        l_name.append(i["name"].strip())
        location_name = i["name"].strip()
        address = i["streetAddress"]
        city = i["city"]
        state = i["state"]
        zip = i["postalCode"]
        country_code = i["country"]
        store_number = i["id"]
        phone = i["phone"]
        lat = i["lat"]
        lng = i["lng"]
        page_url = (
            "https://www.larsensrestaurants.com/" + str(i["slug"]) + "-california"
        )

        h_list = []
        for i in range(len(hours_list)):
            if l_name[i] == location_name:
                h_list.append(hours_list[i])

        hour = " ".join(h_list)

        if "Currently Remodeling" in hour:
            location_name = location_name + " (Currently Remodeling)"
        hour = hour.replace("**Currently Remodeling**", "")
        hour = (re.sub("Due to.+ DoorDash. ", " ", hour)).strip()
        hour = hour.split("Due to")[0].strip()
        hour = (re.sub(" +", " ", hour)).strip()

        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour)
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

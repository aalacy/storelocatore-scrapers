import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

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

    addressess = []
    base_url = "https://www.kia.ca/"
    ca_state = {
        "Newfoundland and Labrador": "nl",
        "Prince Edward Island": "pe",
        "Nova Scotia": "ns",
        "New Brunswick": "nb",
        "Quebec": "qc",
        "Ontario": "on",
        "Manitoba": "mb",
        "Saskatchewan": "sk",
        "Alberta": "ab",
        "British Columbia": "bc",
        "Yukon": "yt",
        "Northwest Territories": "nt",
        "Nunavut": "nu",
    }
    city_list = session.get(
        "https://www.kia.ca/api/finddealer/getCities?searchText=&prov=ON&lang=0"
    ).json()
    for cty in city_list:

        url = (
            "https://www.kia.ca/api/finddealer/getdealers?lang=en&province="
            + str(ca_state[cty.split(",")[-1].strip()])
            + "&city="
            + str(cty.split(",")[0].strip().replace(" ", "+"))
            + "&pc=&dealername=&isEv=0&isPremium=0&dealercode="
        )

        if cty.split(",")[0].strip().replace(" ", "+") == "Notre-Dames+des+Pins":
            url = "https://www.kia.ca/api/finddealer/getdealers?lang=en&province=qc&city=Notre-Dames+des+Pins%2C+Beauce&pc=&dealername=&isEv=0&isPremium=0&dealercode="

        json_data = session.get(url).json()["DealersInfo"][0]

        location_name = json_data["DealerName"]
        street_address = (
            (json_data["Address1"] + str(json_data["Address2"]))
            .replace("None", "")
            .strip()
        )
        city = json_data["City"]
        state = json_data["Province"]
        zipp = json_data["PostalCode"]
        store_number = json_data["Id"]
        phone = json_data["Phone"]
        lat = json_data["Lat"]
        lng = json_data["Lng"]
        page_url = json_data["Website"]

        sales_hours = ""
        service_hours = ""

        try:
            for hr in json_data["WorkingHours"]["DealerTiming"]:
                sales_hours += " " + hr["Day"] + " " + hr["SalesHours"] + " "
                service_hours += " " + hr["Day"] + " " + hr["ServiceHours"] + " "
            hours = (
                "Sales Hours : "
                + sales_hours.strip()
                + " Parts & Service Hours : "
                + service_hours.strip()
            )
        except:
            hours = "<MISSING>"

        if page_url == "http://www.kiamegantic.com/fr":
            page_url = "https://www.audetkiamegantic.com/eng/"
            soup = BeautifulSoup(session.get(page_url).text, "lxml")
            hours = re.sub(
                r"\s+",
                " ",
                " ".join(
                    list(
                        soup.find(
                            "div", {"id": "map_open_hours"}
                        ).ul.li.div.stripped_strings
                    )
                )
                + " "
                + " ".join(
                    list(
                        soup.find("div", {"id": "map_open_hours"})
                        .ul.find_all("li")[1]
                        .stripped_strings
                    )
                ),
            )
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("CA")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)

        store = [str(x).strip() if x else "<MISSING>" for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

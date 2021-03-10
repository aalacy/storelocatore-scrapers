import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("usbank_com")


session = SgRequests()


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
    base_url = "https://schema.milestoneinternet.com/schema/locations.usbank.com/index.html/schema.json"
    loc = session.get(base_url).json()
    addressess = []
    locator_domain = "https://www.usbank.com"
    for data in loc:
        if "areaServed" in data:
            for states in data["areaServed"]:
                link = (
                    "https://schema.milestoneinternet.com/schema/locations.usbank.com/index/"
                    + states.lower().replace(" ", "-")
                    + ".html"
                    + "/schema.json"
                )
                try:
                    all_state = session.get(link).json()
                except:
                    pass
                for st in all_state:
                    if "areaServed" in st and st["areaServed"] != []:
                        for loc1 in st["areaServed"]:
                            store_link = (
                                "https://schema.milestoneinternet.com/schema/locations.usbank.com/index/"
                                + str(states.lower().replace(" ", "-"))
                                + "/"
                                + str(loc1.lower().replace(" ", "-"))
                                + ".html/schema.json"
                            )
                            try:
                                new_request = session.get(store_link).json()
                            except:
                                pass
                            for q in new_request:
                                if "" in q:
                                    for add in q[""]:
                                        page_url = add["url"]
                                        new_request1 = session.get(
                                            add["url"], verify=False
                                        )
                                        soup1 = BeautifulSoup(new_request1.text, "lxml")
                                        try:
                                            json_data = json.loads(
                                                soup1.find(
                                                    "script",
                                                    {"type": "application/ld+json"},
                                                ).text
                                            )
                                            for json1 in json_data:
                                                latitude = json1["geo"]["latitude"]
                                                longitude = json1["geo"]["longitude"]
                                        except:
                                            latitude = ""
                                            longitude = ""
                                        try:
                                            Lobby = " ".join(
                                                list(
                                                    soup1.find(
                                                        "div", {"class": "branchLobby"}
                                                    ).stripped_strings
                                                )
                                            )
                                        except:
                                            Lobby = ""
                                        try:
                                            Drive = " ".join(
                                                list(
                                                    soup1.find(
                                                        "div", {"class": "branchDrive"}
                                                    ).stripped_strings
                                                )
                                            )
                                        except:
                                            Drive = ""
                                        hours_of_operation = Lobby + " " + Drive
                                        phone = add["telephone"]
                                        location_name = add["name"].replace(
                                            "and ATM", ""
                                        )
                                        store = []
                                        street_address = add["address"]["streetAddress"]
                                        city = add["address"]["addressLocality"]
                                        state = add["address"]["addressRegion"]
                                        zipp = add["address"]["postalCode"]
                                        country_code = "US"
                                        if "Branch  and ATM" in location_name:
                                            location_type = "Branch  and ATM"
                                        elif "Branch" in location_name:
                                            location_type = "Branch"
                                        elif "ATM" in location_name:
                                            location_type = "ATM"
                                        store.append(
                                            locator_domain
                                            if locator_domain
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            location_name.strip().lstrip()
                                            if location_name
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            street_address.strip().lstrip()
                                            if street_address
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            city.strip() if city else "<MISSING>"
                                        )
                                        store.append(
                                            state.strip() if state else "<MISSING>"
                                        )
                                        store.append(zipp if zipp else "<MISSING>")
                                        store.append(
                                            country_code
                                            if country_code
                                            else "<MISSING>"
                                        )
                                        store.append("<MISSING>")
                                        store.append(
                                            phone.replace(
                                                "619.-40.1-33", "619.401.3300"
                                            )
                                            .replace("402.-36.7-70", "402.367.7014")
                                            .replace("509.-48.8-33", "509.488.3353")
                                            .replace("618.-59.4-45", "<MISSING>")
                                            if phone
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            location_type
                                            if location_type
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            latitude.replace(",", "")
                                            if latitude
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            longitude if longitude else "<MISSING>"
                                        )
                                        store.append(
                                            hours_of_operation.strip().lstrip()
                                            if hours_of_operation.strip().lstrip()
                                            else "<MISSING>"
                                        )
                                        store.append(
                                            page_url.strip().lstrip()
                                            if page_url.strip().lstrip()
                                            else "<MISSING>"
                                        )
                                        if store[2] in addressess:
                                            continue
                                        addressess.append(store[2])
                                        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("usbank_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    addressess = []
    base_url = "https://schema.milestoneinternet.com/schema/locations.usbank.com/index.html/schema.json"
    loc = session.get(base_url).json()
    for states in loc[0]["areaServed"]:
        state_url = (
            "https://locations.usbank.com/index/"
            + states.lower().replace(" ", "-")
            + ".html"
        )

        state_request = session.get(state_url)
        state_soup = BeautifulSoup(state_request.text, "lxml")
        for citi in state_soup.find_all("li", {"class": "cityListItemLi"}):
            try:
                city_link = "https://locations.usbank.com" + citi.find("a")["href"]
            except:
                continue

            city_request = session.get(city_link)
            city_soup = BeautifulSoup(city_request.text, "lxml")
            for branch in city_soup.find_all(
                "a", {"class": "btn btn-branch-default btn-top"}
            ):

                try:
                    branch_link = "https://locations.usbank.com" + branch["href"]
                except:
                    branch_link = "<MISSING>"

                branch_request = session.get(branch_link)
                branch_soup = BeautifulSoup(branch_request.text, "lxml")
                try:
                    location_name = branch_soup.find(
                        "div", {"class": "branchNam hidden-xs"}
                    ).text
                    try:
                        phone = (
                            branch_soup.find(
                                "div", {"class": "h5heading branchNo hidden-xs"}
                            )
                            .find("a")
                            .text
                        )
                    except:
                        phone = "<MISSING>"
                except:
                    try:
                        addr = list(
                            branch_soup.find(
                                "div",
                                {
                                    "class": "aem-Grid aem-Grid--12 aem-Grid--default--12 aem-Grid--phone--12"
                                },
                            ).stripped_strings
                        )
                        location_name = addr[0]
                        phone = addr[-1]
                    except:
                        phone = "<MISSING>"
                if branch_soup.find("div", {"class": "tempClosedBranch"}):
                    hours_of_operation = "<MISSING>"

                try:
                    try:
                        Lobby = " ".join(
                            list(
                                branch_soup.find(
                                    "div", {"class": "branchLobby"}
                                ).stripped_strings
                            )
                        )
                    except:
                        Lobby = " ".join(
                            list(
                                branch_soup.find_all(
                                    "div",
                                    {
                                        "class": "text parbase aem-GridColumn aem-GridColumn--default--12"
                                    },
                                )[1].stripped_strings
                            )
                        )
                except:
                    Lobby = " "

                try:
                    Drive = " ".join(
                        list(
                            branch_soup.find(
                                "div", {"class": "branchDrive"}
                            ).stripped_strings
                        )
                    )
                except:
                    Drive = ""
                try:
                    hours_of_operation = (
                        (Lobby + " " + Drive)
                        .replace("Â Â", "")
                        .replace("\n", "")
                        .replace("\t", "")
                    )
                    if (
                        "services or performance of U.S. Bancorp Investments."
                        in hours_of_operation
                    ):
                        hours_of_operation = hours_of_operation.split(
                            "services or performance of U.S. Bancorp Investments."
                        )[1]

                except:
                    hours_of_operation = "<MISSING>"

                if hours_of_operation == "":
                    hours_of_operation = "<MISSING>"

                try:
                    json_data = json.loads(
                        branch_soup.find("script", {"type": "application/ld+json"}).text
                    )
                    for val in json_data:
                        street_address = val["address"]["streetAddress"]
                        city = val["address"]["addressLocality"]
                        state = val["address"]["addressRegion"]
                        try:
                            zipp = val["address"]["postalCode"]
                        except:
                            zipp = "<MISSING>"

                        latitude = val["geo"]["latitude"]
                        longitude = val["geo"]["longitude"]
                        store_number = val["branchCode"]
                except:
                    street_address = branch_soup.find(
                        "div", {"class": "h5heading branchStr"}
                    ).text
                    addr = (
                        branch_soup.find("div", {"class": "h5heading branchLoc"})
                        .text.replace("\n", "")
                        .replace("\t", "")
                    )
                    city = addr.split(",")[0]
                    state = addr.split(",")[1].split(" ")[0]
                    try:
                        zipp = addr.split(",")[1].split(" ")[1]
                    except:
                        zipp = "<MISSING>"

                    coord = branch_soup.find_all("script")[4].text.strip().split(";")
                    latitude = coord[0].split("=")[1].strip()
                    longitude = coord[1].split("=")[1].strip()
                    store_number = "<MISSING>"

                store = []
                store.append("https://www.usbank.com/")
                store.append(
                    location_name.strip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                    if location_name
                    else "<MISSING>"
                )
                store.append(
                    street_address.strip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                    if street_address
                    else "<MISSING>"
                )
                store.append(
                    city.strip().replace("\n", "").replace("\t", "").replace("\r", "")
                    if city
                    else "<MISSING>"
                )
                store.append(
                    state.strip().replace("\n", "").replace("\t", "").replace("\r", "")
                    if state
                    else "<MISSING>"
                )
                store.append(
                    zipp.replace("\n", "").replace("\t", "").replace("\r", "")
                    if zipp.replace("\n", "").replace("\t", "").replace("\r", "")
                    else "<MISSING>"
                )
                store.append("US")
                store.append(store_number if store_number else "<MISSING>")
                store.append(
                    phone.replace("619.-40.1-33", "619.401.3300")
                    .replace("402.-36.7-70", "402.367.7014")
                    .replace("509.-48.8-33", "509.488.3353")
                    .replace("618.-59.4-45", "<MISSING>")
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                    if phone
                    else "<MISSING>"
                )
                store.append("Branch and ATM")
                store.append(latitude.replace(",", "") if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                if (
                    hours_of_operation.strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                    != ""
                ):
                    store.append(
                        hours_of_operation.strip()
                        .lstrip()
                        .replace("\n", "")
                        .replace("\t", "")
                        .replace("\r", "")
                        if hours_of_operation
                        else "<MISSING>"
                    )
                else:
                    store.append("<MISSING>")
                store.append(
                    branch_link.strip()
                    .lstrip()
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("\r", "")
                    if branch_link
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

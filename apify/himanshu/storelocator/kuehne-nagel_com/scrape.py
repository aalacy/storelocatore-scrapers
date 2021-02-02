import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as BS
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kuehne-nagel_com")
session = SgRequests()
base_url = "http://kuehne-nagel.com"


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
    for index, url in enumerate(
        [
            "https://ca.kuehne-nagel.com/en_gb/other-links/our-locations-in-canada/",
            "https://us.kuehne-nagel.com/search?query=united%20states",
        ]
    ):
        if index == 0:
            soup = BS(session.get(url).text, "lxml")
            json_data = ""
            try:
                json_data = json.loads(
                    json.loads(
                        soup.find(
                            lambda tag: (tag.name == "script")
                            and "var inlineSettings =" in tag.text
                        )
                        .text.split("var inlineSettings =")[1]
                        .split("if (typeof")[0]
                        .replace("};", "}")
                        .strip()
                    )["locationList"]
                )
            except:
                pass
            for data in json_data:
                location_name = data["locationName"]
                street_address = (
                    data["buildingNo"]
                    + " "
                    + data["street"].replace("\r", "").replace("\n", "")
                )
                if data["addressLine1"]:
                    street_address += " " + data["addressLine1"]
                if data["addressLine2"]:
                    street_address += " " + data["addressLine2"]
                city = data["city"]
                state = data["stateRegion"]
                zipp = data["postalCode"]
                country_code = data["country"]
                store_number = data["uid"]
                phone = data["phoneNumber"].split("or")[0].split("x")[0]
                location_type = data["locationType"]
                lat = data["latitude"]
                lng = data["longitude"]
                hours = (
                    data["openingHours"]
                    .replace("\r", "")
                    .replace("\n", "")
                    .replace("\t", "")
                    .replace("Mo  Fr", "Mo-Fr")
                )
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(country_code)
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(url)
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store
        elif index == 1:
            soup = BS(session.get(url).text, "lxml")
            for dt in soup.find_all("div", {"class": "bg-white component"}):
                if (
                    dt.find("p", {"class": "location__address text-14 mb-0"})
                    is not None
                ):
                    if (
                        "United States"
                        in dt.find(
                            "p", {"class": "location__address text-14 mb-0"}
                        ).text
                    ):
                        adr = list(
                            dt.find(
                                "p", {"class": "location__address text-14 mb-0"}
                            ).stripped_strings
                        )
                        location_name = " ".join(
                            list(dt.find("h3", {"class": "mb-3"}).stripped_strings)
                        )
                        hours_of_operation = ""
                        try:
                            hours_of_operation = " ".join(
                                list(
                                    dt.find(
                                        "p", {"class": "location__hours text-14 mb-0"}
                                    ).stripped_strings
                                )
                            )
                        except:
                            hours_of_operation = ""
                        zipp = adr[1].split()[0]
                        city = " ".join(adr[1].split()[1:])
                        street_address = adr[0]
                        phone = (
                            list(
                                dt.find(
                                    "p", {"class": "location__phone text-14 mb-0"}
                                ).stripped_strings
                            )[0]
                            .replace("Phone", "")
                            .replace("x2002", "")
                        )
                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append("<MISSING>")
                        store.append(zipp)
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        store.append("<MISSING>")
                        store.append(
                            hours_of_operation.replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .replace("Mo  Fr:", "Mo-Fr")
                        )
                        store.append("<MISSING>")
                        store = [
                            str(x).replace("\n", "").replace("\r", "").replace("–", "-")
                            if x
                            else "<MISSING>"
                            for x in store
                        ]
                        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

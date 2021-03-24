import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as BS
from sglogging import SgLogSetup
from geopy.geocoders import Nominatim
import re

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
            "https://ca.kuehne-nagel.com/locations?query=canada",
            "https://uk.kuehne-nagel.com/locations?query=%22United%20Kingdom%22",
            "https://us.kuehne-nagel.com/search?query=united%20states",
        ]
    ):
        if index == 0:
            soup = BS(session.get(url).text, "lxml")
            for dt in soup.find_all("div", {"class": "bg-white component"}):
                if (
                    dt.find("p", {"class": "location__address text-14 mb-0"})
                    is not None
                ):
                    if (
                        "Canada"
                        in dt.find(
                            "p", {"class": "location__address text-14 mb-0"}
                        ).text
                    ):
                        page_url = "https://home.kuehne-nagel.com/locations"
                        adr = list(
                            dt.find(
                                "p", {"class": "location__address text-14 mb-0"}
                            ).stripped_strings
                        )
                        location_name = dt.find("h3", {"class": "mb-3"}).text
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
                        postal_code = "".join(adr[1])
                        temp_zipp = re.search(r"[A-Z]\d[A-Z]\s\d[A-Z]\d", postal_code)
                        a = temp_zipp.group(0)
                        if len(a) == 7:
                            zipp = a
                        else:
                            zipp = "<MISSING>"
                        city = adr[1].split(" ")[-1]
                        street_address = adr[0]
                        if "Water St 354" in street_address:
                            city = "St. John's"
                        geolocator = Nominatim(user_agent="myGeocoder")
                        location = geolocator.geocode(street_address)
                        try:
                            latitude = location.latitude
                        except:
                            latitude = "<MISSING>"
                        try:
                            longitude = location.longitude
                        except:
                            longitude = "<MISSING>"

                        phone = (
                            list(
                                dt.find(
                                    "p", {"class": "location__phone text-14 mb-0"}
                                ).stripped_strings
                            )[0]
                            .replace("Phone", "")
                            .strip()
                            .split("or")[0]
                        )

                        try:
                            location_type = (
                                dt.find("p", class_="location__service text-14 mb-0")
                                .text.replace("Types of Service", "")
                                .strip()
                            )
                        except:
                            location_type = "<MISSING>"

                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append("<MISSING>")
                        store.append(zipp)
                        store.append("CA")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append(location_type)
                        store.append(latitude)
                        store.append(longitude)
                        store.append(
                            hours_of_operation.replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .replace("Opening Hours", "")
                            if hours_of_operation
                            else "<MISSING>"
                        )
                        store.append(page_url)
                        store = [
                            str(x)
                            .replace("\n", " ")
                            .replace("\r", "")
                            .replace("–", "-")
                            if x
                            else "<MISSING>"
                            for x in store
                        ]
                        store = [
                            x.replace("\n", " ").replace("\t", "").replace("\r", "")
                            if type(x) == str
                            else x
                            for x in store
                        ]
                        yield store

        elif index == 1:
            page_url = "https://home.kuehne-nagel.com/locations"
            soup = BS(session.get(url).text, "lxml")
            for dt in soup.find_all("div", {"class": "bg-white component"}):
                if (
                    dt.find("p", {"class": "location__address text-14 mb-0"})
                    is not None
                ):
                    if (
                        "United Kingdom"
                        in dt.find(
                            "p", {"class": "location__address text-14 mb-0"}
                        ).text
                    ):
                        adr = list(
                            dt.find(
                                "p", {"class": "location__address text-14 mb-0"}
                            ).stripped_strings
                        )
                        location_name = dt.find("h3", {"class": "mb-3"}).text
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
                        temp_zipp1 = adr[1].split(" ")
                        zipp = temp_zipp1[0] + temp_zipp1[1]
                        city = adr[1].split(" ")[-1]
                        street_address = adr[0]
                        if "Hall Wood Avenue" in street_address:
                            city = "St. Helens"
                        geolocator = Nominatim(user_agent="myGeocoder")
                        location = geolocator.geocode(street_address)
                        try:
                            latitude = location.latitude
                        except:
                            latitude = "<MISSING>"
                        try:
                            longitude = location.longitude
                        except:
                            longitude = "<MISSING>"

                        phone = (
                            list(
                                dt.find(
                                    "p", {"class": "location__phone text-14 mb-0"}
                                ).stripped_strings
                            )[0]
                            .replace("Phone", "")
                            .split("or")[0]
                            .strip()
                        )
                        try:
                            location_type = (
                                dt.find("p", class_="location__service text-14 mb-0")
                                .text.replace("Types of Service", "")
                                .strip()
                                .replace(
                                    "https://uk.kuehne-nagel.com/en_gb/birmingham/",
                                    "<MISSING>",
                                )
                            )
                        except:
                            location_type = "<MISSING>"

                        store = []
                        store.append(base_url)
                        store.append(location_name)
                        store.append(street_address)
                        store.append(city)
                        store.append("<MISSING>")
                        store.append(zipp)
                        store.append("UK")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append(location_type)
                        store.append(latitude)
                        store.append(longitude)
                        store.append(
                            hours_of_operation.replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .replace("Opening Hours", "")
                            if hours_of_operation
                            else "<MISSING>"
                        )
                        store.append(page_url)
                        store = [
                            str(x)
                            .replace("\n", " ")
                            .replace("\r", "")
                            .replace("–", "-")
                            if x
                            else "<MISSING>"
                            for x in store
                        ]
                        store = [
                            x.replace("\n", " ").replace("\t", "").replace("\r", "")
                            if type(x) == str
                            else x
                            for x in store
                        ]
                        yield store

        elif index == 2:
            page_url = "https://home.kuehne-nagel.com/locations"
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

                        geolocator = Nominatim(user_agent="myGeocoder")
                        location = geolocator.geocode(street_address + "," + city)
                        try:
                            latitude = location.latitude
                        except:
                            latitude = "<MISSING>"
                        try:
                            longitude = location.longitude
                        except:
                            longitude = "<MISSING>"

                        phone = (
                            list(
                                dt.find(
                                    "p", {"class": "location__phone text-14 mb-0"}
                                ).stripped_strings
                            )[0]
                            .replace("Phone", "")
                            .replace("x2002", "")
                            .replace("x227", "")
                        )

                        try:
                            location_type = (
                                dt.find("p", class_="location__service text-14 mb-0")
                                .text.replace("Types of Service", "")
                                .strip()
                            )
                        except:
                            location_type = "<MISSING>"
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
                        store.append(location_type)
                        store.append(latitude)
                        store.append(longitude)
                        store.append(
                            hours_of_operation.replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .replace("Mo  Fr:", "Mo-Fr")
                            .replace("Opening Hours", "")
                            if hours_of_operation
                            else "<MISSING>"
                        )
                        store.append(page_url)
                        store = [
                            str(x)
                            .replace("\n", " ")
                            .replace("\r", "")
                            .replace("–", "-")
                            if x
                            else "<MISSING>"
                            for x in store
                        ]
                        store = [
                            x.replace("\n", " ").replace("\t", "").replace("\r", "")
                            if type(x) == str
                            else x
                            for x in store
                        ]
                        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

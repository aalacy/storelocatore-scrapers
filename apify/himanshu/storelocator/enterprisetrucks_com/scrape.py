import csv

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
    base_url = "https://www.enterprisetrucks.com"
    r = session.get(base_url + "/truckrental/en_US/locations.html")
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", {"id": "allUSLocations"}).find_all("a")
    for atag in main:
        page_url = base_url + atag["href"]
        r1 = session.get(base_url + atag["href"])
        soup1 = BeautifulSoup(r1.text, "lxml")
        if "Our apologies…an unexpected error occurred." not in r1.text:
            try:
                location_name = soup1.find("input", {"id": "location_name"})["value"]
            except TypeError:
                continue
            street_address = soup1.find("input", {"id": "location_address"})["value"]
            addr = soup1.find("input", {"id": "location_address2"})["value"]
            city = addr.split(",")[0]
            state = addr.split(",")[1].strip().split(" ")[0]
            try:
                zipp = addr.split(",")[1].strip().split(" ")[1]
                if len(zipp) < 5:
                    zipp = "<MISSING>"
            except:
                zipp = "<MISSING>"
            phone = soup1.find("input", {"id": "location_phone"})["value"]
            try:
                latitude = soup1.find("input", {"id": "location_latitude"})["value"]
                longitude = soup1.find("input", {"id": "location_longitude"})["value"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            hours_of_operation = " ".join(
                list(
                    soup1.find("table", {"class": "businessHours"})
                    .find("tbody")
                    .stripped_strings
                )
            )
            store = []
            store.append("https://www.enterprisetrucks.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store
    base_url = "https://www.enterprisetrucks.com"
    r = session.get(base_url + "/truckrental/en_US/locations.html")
    soup = BeautifulSoup(r.text, "lxml")
    main = soup.find("div", {"id": "allCALocations"}).find_all("a")
    for atag in main:
        page_url = base_url + atag["href"]
        r1 = session.get(base_url + atag["href"])
        soup1 = BeautifulSoup(r1.text, "lxml")
        if "Our apologies…an unexpected error occurred." not in r1.text:
            try:
                location_name = soup1.find("input", {"id": "location_name"})["value"]
            except TypeError:
                continue
            street_address = soup1.find("input", {"id": "location_address"})["value"]
            addr = soup1.find("input", {"id": "location_address2"})["value"]
            city = addr.split(",")[0]
            state = addr.split(",")[1].strip().split(" ")[0]
            zipp = " ".join(addr.split(",")[1].strip().split(" ")[-2:])
            if len(zipp) < 5:
                zipp = "<MISSING>"
            phone = soup1.find("input", {"id": "location_phone"})["value"]
            try:
                latitude = soup1.find("input", {"id": "location_latitude"})["value"]
                longitude = soup1.find("input", {"id": "location_longitude"})["value"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            hours_of_operation = " ".join(
                list(
                    soup1.find("table", {"class": "businessHours"})
                    .find("tbody")
                    .stripped_strings
                )
            )
            store = []
            store.append("https://www.enterprisetrucks.com")
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

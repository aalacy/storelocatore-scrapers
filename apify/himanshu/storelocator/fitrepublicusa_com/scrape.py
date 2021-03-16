import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("fitrepublicusa_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    base_url = "https://www.fitrepublicusa.com/"
    r = session.get("https://www.fitrepublicusa.com/locations")
    soup = BeautifulSoup(r.text, "lxml")
    k = soup.find(
        "div",
        {
            "class": "sqs-block html-block sqs-block-html",
            "id": "block-17db0418b04d7073c0cc",
        },
    ).find_all("p")
    _dict = {}
    for i in k:
        store = []
        kp = i.find("a")
        if kp != None:
            link = kp["href"]

            if "map=" in link:
                lat = link.split("map=")[-1].split(",")[0]
                lng = i.find("a")["href"].split("map=")[-1].split(",")[1]
                _dict[i.find("strong").text] = {"lat": lat, "lng": lng}
            elif len(i.find_all("a")) > 1 and "map=" in i.find_all("a")[1]["href"]:
                lat = i.find_all("a")[1]["href"].split("map=")[-1].split(",")[0]
                lng = i.find_all("a")[1]["href"].split("map=")[-1].split(",")[1]
                _dict[i.find("strong").text] = {"lat": lat, "lng": lng}
            else:
                lat = "<MISSING>"
                lng = "<MISSING>"
        else:
            lat = "<MISSING>"
            lng = "<MISSING>"
    data = list(
        soup.find_all("div", {"class": "sqs-block-content"})[3].stripped_strings
    )
    del data[0]
    for i in range(0, len(data), 4):
        location_name = data[i]
        if location_name in _dict:
            latitude = _dict[location_name]["lat"]
            longitude = _dict[location_name]["lng"]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        street_address = data[i + 1].split("-")[0]
        phone = " ".join(data[i + 1].split("-")[1:]).strip()
        city = data[i + 2].split(",")[0]
        if len(data[i + 2].split(",")) == 2:
            state = data[i + 2].split(",")[1].split(" ")[1]
            zipp = data[i + 2].split(",")[1].split(" ")[-1].replace("MO", "64468")
        else:
            state = data[i + 2].split(",")[1].strip()
            zipp = data[i + 2].split(",")[2].strip()

        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append("https://www.fitrepublicusa.com/locations")

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

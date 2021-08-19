import csv
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


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
            if row:
                writer.writerow(row)


def fetch_data():

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    data = []
    location_name = []
    city = []
    street_address = []
    zipcode = []
    state = []
    lat = []
    long = []
    hours_of_operation = []
    phone = []
    links = []

    base_link = "https://www.pinktaco.com/locations"
    req = session.get(base_link, headers=headers)

    base = BeautifulSoup(req.text, "lxml")

    stores = base.find_all(class_="location")
    store_text = [stores[n].text for n in range(0, len(stores))]
    store_links = [
        "https://www.pinktaco.com" + stores[n].a["href"] for n in range(0, len(stores))
    ]
    coords = re.findall(r"LatLng = \[ *(-?[\d\.]+), *(-?[\d\.]+)\];", str(base))
    for n in range(0, len(store_links)):
        if "COMING SOON" not in store_text[n].upper():
            req = session.get(store_links[n], headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name.append(store_text[n].replace("\n", ""))
            try:
                street = base.find(class_="details").p.text
                city_str = (
                    base.find(class_="details")
                    .find_all("p")[1]
                    .text.split(",")[0]
                    .strip()
                )
                state_str = (
                    base.find(class_="details")
                    .find_all("p")[1]
                    .text.split(",")[1]
                    .split()[0]
                    .strip()
                )
                zip_str = (
                    base.find(class_="details")
                    .find_all("p")[1]
                    .text.split(",")[1]
                    .split()[1]
                    .strip()
                )
                phone_str = base.find(class_="details").find_all("p")[2].text.strip()
            except:
                street = base.find(class_="details").p.text.split(",")[0]
                city_str = base.find(class_="details").p.text.split(",")[1].strip()
                state_str = (
                    base.find(class_="details").p.text.split(",")[2].split()[0].strip()
                )
                zip_str = (
                    base.find(class_="details").p.text.split(",")[2].split()[1].strip()
                )
                phone_str = base.find(class_="details").find_all("p")[1].text.strip()
            city.append(city_str)
            state.append(state_str)
            zipcode.append(zip_str)
            phone.append(phone_str)
            street_address.append(street)

            hours = base.find(class_="details")
            if "RESTAURANT HOURS" in hours.text.upper():
                hour = (
                    hours.text.upper()
                    .split("RESTAURANT HOURS")[1]
                    .strip()
                    .split("HOUR")[0]
                    .replace("\n", " ")
                    .strip()
                )
                hours_of_operation.append(" ".join(hour.split()[:-1]))
            else:
                hours_of_operation.append("<MISSING>")

            lati, longi = coords[n]

            lat.append(lati)
            long.append(longi)

            links.append(store_links[n])

    for n in range(0, len(location_name)):
        data.append(
            [
                "https://www.pinktaco.com",
                location_name[n],
                street_address[n],
                city[n],
                state[n],
                zipcode[n],
                "US",
                "<MISSING>",
                phone[n],
                "<MISSING>",
                lat[n],
                long[n],
                hours_of_operation[n],
                links[n],
            ]
        )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

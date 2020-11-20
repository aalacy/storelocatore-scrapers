from bs4 import BeautifulSoup
import csv
import re
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("dangelos_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data1 = []
    url = "https://dangelos.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.findAll("li", {"class": "location-result"})
    for data in data_list:
        title = data["data-name"]
        lat = data["data-latitude"]
        longt = data["data-longitude"]
        link = data.find("a", {"class": "location-title"})
        if re.match(r"^http", link["href"]):
            link = link["href"]
        else:
            link = "https://dangelos.com" + link["href"]
        store = link
        store = store.split("location/")[1]
        store = store.split("/")[0]
        if store.isdigit() is True:
            store = store
        else:
            store = "<MISSING>"
        phone = data.find("span", {"class": "location-phone"})
        if phone is None:
            phone = data.find("a", {"class": "location-phone"}).text
        else:
            phone = phone.text
        hours_list = data.find("div", {"class": "location-hours"})
        hours_list = hours_list.findAll("tr")
        hours = ""
        for temp in hours_list:
            day = temp.find("span").text
            temp_hour = temp.find("td").text
            temp_hour = temp_hour.strip()
            hours = hours + day + " " + temp_hour + " "
        address = data["data-address"]
        address = address.replace(",", " ")
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("Occupancy") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        data1.append(
            [
                "https://www.foodmaxx.com/",
                "https://www.foodmaxx.com/stores",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )
    return data1


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

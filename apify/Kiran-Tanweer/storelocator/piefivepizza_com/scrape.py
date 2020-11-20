from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("piefivepizza_com")

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
    data = []
    url = "https://www.piefivepizza.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    data_list = soup.findAll("div", {"class": "location-map-select"})
    places = data_list[0].findAll("area")
    for p in places:
        statelink = p.get("href")
        r = session.get(statelink, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        numOfLocs = soup.findAll("hr")
        for num in range(0, len(numOfLocs)):
            locName = soup.findAll("span", {"class": "loc-name"})[num]
            title = locName.text
            phone = soup.findAll("span", {"class": "loc-phone"})[num]
            phone = phone.text
            phone = phone.replace(") ", "-")
            phone = phone.replace("(", "")
            words = phone.split(" ")
            phone = words[1]
            street = soup.findAll("span", {"class": "loc-address-1"})[num]
            street = street.text
            city = soup.findAll("span", {"class": "loc-address-3"})[num]
            city = city.text
            location = city.split(",")
            city = location[0]
            location = location[1]
            location = location.lstrip()
            words = location.split(" ")
            state = words[0]
            zcode = words[1]
            hours = soup.findAll("span", {"loc-hours"})[num]
            hours = hours.text
            if hours == "Delivery provided by DoorDash":
                hours = "<MISSING>"
            hours = hours.replace(":", "")
            hours = hours.replace(";", "")

            data.append(
                [
                    "https://www.piefivepizza.com/locations/",
                    statelink,
                    title,
                    street,
                    city,
                    state,
                    zcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    "<INACCESSIBLE>",
                    "<INACCESSIBLE>",
                    hours,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

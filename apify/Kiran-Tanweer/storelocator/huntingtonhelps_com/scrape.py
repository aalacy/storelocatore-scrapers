from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup
import time
import csv


logger = SgLogSetup().get_logger("huntingtonhelps_com")

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
    statelist = [
        "AL",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NJ",
        "NM",
        "NY",
        "NC",
        "OH",
        "OK",
        "OR",
        "PA",
        "SC",
        "TN",
        "TX",
        "UT",
        "VA",
        "WA",
        "WI",
    ]
    url = "https://huntingtonhelps.com/location/state-list"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"id": "centerListing"})
    for state in statelist:
        subdivlist = divlist.find("div", {"id": state})
        location = subdivlist.findAll("div", {"class": "listing__item"})
        for loc in location:
            title = loc.find("h3").text
            address = loc.findAll("div", {"class": "address"})
            street = address[0].text
            address2 = address[1].text
            city, address2 = address2.split(",")
            city = city.lstrip()
            city = city.rstrip()
            address2 = address2.lstrip()
            address2 = address2.rstrip()
            state, zipcode = address2.split(" ")
            state = state.lstrip()
            state = state.rstrip()
            zipcode = zipcode.lstrip()
            zipcode = zipcode.rstrip()
            phone = loc.find("div", {"class": "phone"}).text
            loclink = loc.find("h3").find("a")["href"]
            loclink = "https://huntingtonhelps.com" + loclink
            link = session.get(loclink, headers=headers, verify=False)
            soup = BeautifulSoup(link.text, "html.parser")
            hour = soup.find("div", {"class": "hours col-sm-6"})
            li = hour.findAll("li")
            hours = ""
            for ele in li:
                hr = ele.text
                hours = hours + " " + hr
            hours = hours.lstrip()
            hours = hours.rstrip()

            data.append(
                [
                    "https://huntingtonhelps.com/",
                    loclink,
                    title,
                    street,
                    city,
                    state,
                    zipcode,
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
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

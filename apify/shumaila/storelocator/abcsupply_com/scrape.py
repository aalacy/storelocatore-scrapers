from bs4 import BeautifulSoup
import csv
import re
from sgrequests import SgRequests

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
    titlelist = []
    pattern = re.compile(r"\s\s+")
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    p = 0
    for i in range(0, len(states)):
        url = "https://www.abcsupply.com/locations/location-results"
        result = session.post(url, data={"State": states[i]})
        soup = BeautifulSoup(result.text, "html.parser")
        divlist = soup.findAll("div", {"class": "location"})
        maplist = result.text.split("var marker = new google.maps.Marker({")[1:]
        for div in divlist:

            title = (
                div.find("div", {"class": "location-name"})
                .text.replace("\n", " ")
                .strip()
            )
            store = (
                div.find("div", {"class": "location-name"})
                .find("a")["id"]
                .split("_", 1)[1]
            )
            link = (
                "https://www.abcsupply.com"
                + div.find("div", {"class": "location-name"}).find("a")["href"]
            )
            address = div.find("div", {"class": "location-address"}).text
            address = re.sub(pattern, "\n", address).strip().splitlines()
            street = address[0]
            try:
                city, state = address[1].split(", ", 1)
            except:
                street = street + " " + address[1]
                city, state = address[2].split(", ", 1)
            state, pcode = state.split(" ", 1)
            phone = address[-1]
            try:
                hours = div.find("div", {"class": "hours-detail"}).text
                hours = re.sub(pattern, " ", hours).strip()
            except:
                hours = "Mon - Fri: 7:00 AM - 5:00 PM"
            lat = longt = "<MISSING>"
            for coord in maplist:
                coord = coord.split(");", 1)[0]
                if title + " - ABC Supply #" + store in coord:
                    lat = coord.split("lat: ", 1)[1].split(",", 1)[0]
                    longt = coord.split("lng: ", 1)[1].split(" }", 1)[0]
                    break
            if store in titlelist:
                continue
            titlelist.append(store)
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(lat) < 3:
                lat = "<MISSING>"
            if len(longt) < 3:
                longt = "<MISSING>"
            data.append(
                [
                    "https://www.abcsupply.com/",
                    link,
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

            p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

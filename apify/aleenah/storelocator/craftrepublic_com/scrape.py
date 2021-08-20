from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("craftrepublic_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "token": "SFNZAIIBLMQAAYVQ",
}

headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.craftrepublic.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "locationLink"})
    for link in linklist:
        if True:
            link = "https://www.craftrepublic.com" + link["href"]
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("title").text.split(":")[0]
            title = re.sub(pattern, "", title)
            title = re.sub(cleanr, "", title)
            address = re.sub(
                cleanr, " ", str(soup.find("div", {"class": "locations-address"}))
            )
            address = address.strip().splitlines()
            street = address[0]
            city, state = address[1].split(", ")
            state, pcode = state.lstrip().split(" ", 1)
            info = soup.findAll("a", {"class": "locationLink2"})
            coords = info[0]["href"]
            phone = info[1].text.strip()
            lat, lng = coords.split("Location/")[1].split("+,")
            if link == "https://www.craftrepublic.com/locations/houston":
                api = "https://api.momentfeed.com/v1/lf/location/store-info/5b6298f2e4b001c538b4a687"
            elif link == "https://www.craftrepublic.com/locations/albuquerque":
                api = "https://api.momentfeed.com/v1/lf/location/store-info/5977c7c8e4b05ecc067d9fa7"
            elif link == "https://www.craftrepublic.com/locations/tucson":
                api = "https://api.momentfeed.com/v1/lf/location/store-info/5b6298f2e4b0f970ebf2c90f"
            p = session.get(api, headers=headers2, verify=False).json()
            hours = p["hours"]
            hours = hours.rstrip(";")
            hours = hours.split(";")
            hoo = ""
            for h in hours:
                h = h.strip()
                m = h.split(",")
                if m[0] == "1":
                    day = "Monday"
                elif m[0] == "2":
                    day = "Tuesday"
                elif m[0] == "3":
                    day = "Wednesday"
                elif m[0] == "4":
                    day = "Thursday"
                elif m[0] == "5":
                    day = "Friday"
                elif m[0] == "6":
                    day = "Saturday"
                elif m[0] == "7":
                    day = "Sunday"
                start_t = m[1]
                end_t = m[2]
                hoo = hoo + " " + day + ": " + start_t + "-" + end_t
            hoo = hoo.strip()
            storeid = p["corporateId"].strip()

            data.append(
                [
                    "https://www.craftrepublic.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    storeid,
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
                    hoo,
                ]
            )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

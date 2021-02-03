import csv
import json
import re
import time

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import sglog

from sgrequests import SgRequests

from sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger(logger_name="hearinglife.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    driver = SgChrome(user_agent=user_agent).chrome()

    base_link = "https://www.hearinglife.com/find-hearing-aid-center"

    driver.get(base_link)
    WebDriverWait(driver, 100).until(
        ec.presence_of_element_located((By.CLASS_NAME, "map-centers-list-item"))
    )
    time.sleep(2)
    base = BeautifulSoup(driver.page_source, "lxml")

    locator_domain = "hearinglife.com"

    data = []

    us_states = {
        "AL": "Alabama",
        "AK": "Alaska",
        "AS": "American Samoa",
        "AZ": "Arizona",
        "AR": "Arkansas",
        "CA": "California",
        "CO": "Colorado",
        "CT": "Connecticut",
        "DE": "Delaware",
        "DC": "District of Columbia",
        "FL": "Florida",
        "GA": "Georgia",
        "GU": "Guam",
        "HI": "Hawaii",
        "ID": "Idaho",
        "IL": "Illinois",
        "IN": "Indiana",
        "IA": "Iowa",
        "KS": "Kansas",
        "KY": "Kentucky",
        "LA": "Louisiana",
        "ME": "Maine",
        "MD": "Maryland",
        "MA": "Massachusetts",
        "MI": "Michigan",
        "MN": "Minnesota",
        "MS": "Mississippi",
        "MO": "Missouri",
        "MT": "Montana",
        "NE": "Nebraska",
        "NV": "Nevada",
        "NH": "New Hampshire",
        "NJ": "New Jersey",
        "NM": "New Mexico",
        "NY": "New York",
        "NC": "North Carolina",
        "ND": "North Dakota",
        "MP": "Northern Mariana Islands",
        "OH": "Ohio",
        "OK": "Oklahoma",
        "OR": "Oregon",
        "PA": "Pennsylvania",
        "PR": "Puerto Rico",
        "RI": "Rhode Island",
        "SC": "South Carolina",
        "SD": "South Dakota",
        "TN": "Tennessee",
        "TX": "Texas",
        "UT": "Utah",
        "VT": "Vermont",
        "VI": "Virgin Islands",
        "VA": "Virginia",
        "WA": "Washington",
        "WV": "West Virginia",
        "WI": "Wisconsin",
        "WY": "Wyoming",
    }

    items = base.find_all(class_="map-centers-list-item")

    log.info("Processing " + str(len(items)) + " links ..")
    for item in items:
        location_name = item.h2.text.strip()

        raw_address = item.p.text.split(",")

        street_address = " ".join(raw_address[:-3]).strip()
        street_address = (re.sub(" +", " ", street_address)).strip()
        street_address = street_address.split("(")[0].strip()
        try:
            digit = re.search(r"\d", street_address).start(0)
            if digit != 0:
                street_address = street_address[digit:]
        except:
            pass

        city = raw_address[-3].strip()
        state = raw_address[-2].strip()
        zip_code = raw_address[-1].strip()
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        phone = item.find(class_="map-center-details-phone").text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        state_link = us_states[state].replace(" ", "-")
        city_link = city.replace(" ", "-")

        link = "https://www.hearinglife.com/hearing-aids-centers/" + state_link + "/" + city_link

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        got_hours = False
        try:
            hours_of_operation = " ".join(list(base.find(class_="hours-list").stripped_strings))
            got_hours = True
        except:
            if "-" in city_link:
                city_link = city_link.replace("-", " ")
                link = "https://www.hearinglife.com/hearing-aids-centers/" + state_link + "/" + city_link
                try:
                    req = session.get(link, headers=headers)
                    base = BeautifulSoup(req.text, "lxml")

                    hours_of_operation = " ".join(list(base.find(class_="hours-list").stripped_strings))
                    got_hours = True
                except:
                    pass
        if got_hours:
            script = base.find('script', attrs={'type': "application/ld+json"}).text.replace('\n', '').strip()
            store = json.loads(script)

            js_street = store["address"]["streetAddress"]

            if street_address[:3] in js_street:
                latitude = store['geo']['latitude']
                longitude = store['geo']['longitude']
            else:
                link = "<INACCESSIBLE>"
                hours_of_operation = "<INACCESSIBLE>"
                latitude = "<INACCESSIBLE>"
                longitude = "<INACCESSIBLE>"
        else:
            link = "<INACCESSIBLE>"
            hours_of_operation = "<INACCESSIBLE>"
            latitude = "<INACCESSIBLE>"
            longitude = "<INACCESSIBLE>"

        data.append(
            [
                locator_domain,
                link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    driver.close()

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

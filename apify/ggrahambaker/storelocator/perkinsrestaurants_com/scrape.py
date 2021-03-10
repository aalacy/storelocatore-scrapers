import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json


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
    session = SgRequests()
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    locator_domain = "https://www.perkinsrestaurants.com/"
    url = "https://stores.perkinsrestaurants.com/"
    ext = "index.html"

    r = session.get(url + ext, headers=HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")

    countries = soup.find_all("li", {"class": "c-directory-list-content-item"})
    c_list = []
    for c in countries:
        c_list.append(url + c.find("a")["href"])
    state_list = []
    city_list = []
    link_list = []
    for c in c_list:
        r = session.get(c, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")
        states = soup.find_all("li", {"class": "c-directory-list-content-item"})
        for state in states:
            link = url + state.find("a")["href"]

            if len(link.split("/")) == 5:
                state_list.append(link)
            elif len(link.split("/")) == 6:
                city_list.append(link)
            else:
                link_list.append(link)
    for state in state_list:
        r = session.get(state, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")
        cities = soup.find_all("li", {"class": "c-directory-list-content-item"})
        for c in cities:
            link = url + c.find("a")["href"].replace("../", "")

            if len(link.split("/")) == 6:
                city_list.append(link)
            else:
                link_list.append(link)
    for city in city_list:
        r = session.get(city, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")
        locs = soup.find_all("h2", {"class": "c-location-grid-item-title"})
        for loc in locs:
            link = url + loc.find("a")["href"].replace("../", "")
            link_list.append(link)
    all_store_data = []
    for link in link_list:
        r = session.get(link, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")

        location_name = soup.find("h1", {"class": "c-location-title"}).text

        lat = soup.find("meta", {"itemprop": "latitude"})["content"]
        longit = soup.find("meta", {"itemprop": "longitude"})["content"]
        street_address = soup.find("span", {"class": "c-address-street-1"}).text
        city = soup.find("span", {"itemprop": "addressLocality"}).text
        state = soup.find("abbr", {"class": "c-address-state"}).text
        zip_code = soup.find("span", {"itemprop": "postalCode"}).text.strip()

        country_code = soup.find("abbr", {"class": "c-address-country-name"}).text

        phone_number = soup.find("a", {"class": "c-phone-number-link"}).text

        hours_json = json.loads(
            soup.find("div", {"class": "c-location-hours-details-wrapper"})["data-days"]
        )
        hours = ""
        for h in hours_json:
            day = h["day"]
            try:
                if h["intervals"][0]["start"] == 0:
                    start = "Midnight"
                else:
                    start = (
                        str(h["intervals"][0]["start"])[:-2]
                        + ":"
                        + str(h["intervals"][0]["start"])[-2:]
                        + " AM "
                    )
                if h["intervals"][0]["end"] == 0:
                    end = "Midnight"
                else:
                    tempend = str(h["intervals"][0]["end"])[:-2]

                    if (int)(str(h["intervals"][0]["end"])[:-2]) > 12:
                        tempend = (str)((int)(tempend) - 12)
                    end = tempend + ":" + str(h["intervals"][0]["end"])[-2:] + " PM "
                if start == "Midnight" and end == "Midnight":
                    hours += day + " Open 24 hours "
                else:
                    hours += day + " " + start + " - " + end + " "
            except:
                hours = hours + day + " " + " Closed "
        hours = hours.strip()
        if hours == "":
            hours = "<MISSING>"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        page_url = link
        store_data = [
            locator_domain,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone_number,
            location_type,
            lat,
            longit,
            hours,
            page_url,
        ]

        all_store_data.append(store_data)
    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

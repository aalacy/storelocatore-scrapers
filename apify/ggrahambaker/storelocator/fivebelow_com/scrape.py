import csv
import json

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
            writer.writerow(row)


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://www.fivebelow.com/"
    url = "https://locations.fivebelow.com/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")

    main = soup.find("section", {"class": "StateList"})
    states = main.find_all("a", {"class": "Directory-listLink"})

    state_list = [url + state["href"] for state in states]

    link_list = []
    city_list = []
    for state in state_list:
        if "/dc/washington" in state:
            city_list.append(state)
            continue
        r = session.get(state, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        cities = soup.find_all("a", {"class": "Directory-listLink"})
        for city in cities:
            city_link = city["href"]
            if len(city_link.split("/")) == 2:
                city_list.append(url + city_link)
            else:
                link_list.append(url + city_link)

    for city in city_list:
        r = session.get(city, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        links = soup.find_all("a", {"class": "Teaser-titleLink"})

        for link in links:
            link_list.append(url + link["href"].replace("../", ""))

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        notifs = soup.find_all("div", {"class": "Notification-text"})
        if len(notifs) > 0:
            continue

        location_name = soup.find("span", {"class": "Hero-locationGeo"}).text
        street_address = soup.find("meta", {"itemprop": "streetAddress"})["content"]
        city = soup.find("meta", {"itemprop": "addressLocality"})["content"]
        state = soup.find("span", {"class": "c-address-state"}).text
        zip_code = soup.find("span", {"class": "c-address-postal-code"}).text

        country_code = "US"

        lat = soup.find("meta", {"itemprop": "latitude"})["content"]
        longit = soup.find("meta", {"itemprop": "longitude"})["content"]

        phone_numbers = soup.find_all("div", {"itemprop": "telephone"})
        if len(phone_numbers) == 1:
            phone_number = phone_numbers[0].text
        else:
            phone_number = "<MISSING>"

        try:
            hours_json = json.loads(
                soup.find("div", {"class": "js-hours-table"})["data-days"]
            )
            hours = ""
            for hour in hours_json:
                day = hour["day"]
                if hour["isClosed"]:
                    hours += day + " Closed "
                else:
                    ints = hour["intervals"][0]
                    start = ints["start"]
                    end = ints["end"]
                    hours += day + " " + str(start) + "-" + str(end) + " "

            hours = hours.strip()
        except:
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

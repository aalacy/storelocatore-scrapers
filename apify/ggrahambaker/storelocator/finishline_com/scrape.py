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

    locator_domain = "https://www.finishline.com/"
    url = "https://stores.finishline.com/index.html"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    states = soup.find_all("a", {"class": "c-directory-list-content-item-link"})
    base_url = "https://stores.finishline.com/"
    state_list = [base_url + state["href"] for state in states]

    city_list = []
    link_list = []

    for state in state_list:
        if len(state.split("/")) == 5:
            city_list.append(state)

        elif len(state.split("/")) == 6:
            link_list.append(state)

        else:
            r = session.get(state, headers=headers)
            soup = BeautifulSoup(r.content, "html.parser")
            cities = soup.find_all("a", {"class": "c-directory-list-content-item-link"})
            for city in cities:
                city_link = base_url + city["href"]
                if len(city_link.split("/")) == 5:
                    city_list.append(city_link)

                else:
                    link_list.append(city_link)

    all_store_data = []
    for city_link in city_list:
        r = session.get(city_link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")

        locs = soup.find_all("div", {"class": "c-location-grid-col"})

        for loc in locs:
            a_tags = loc.find_all("a", {"class": "c-location-grid-item-link"})
            if len(a_tags) == 4:
                link_list.append(a_tags[1]["href"])
                continue

            # store inside macys
            name_brand = loc.find("span", {"class": "location-name-brand"}).text.strip()
            name_loc = loc.find("span", {"class": "location-name-geo"}).text.strip()
            location_name = (name_brand + " " + name_loc).replace("  ", " ").strip()

            hours_json = json.loads(
                loc.find("div", {"class": "js-location-hours"})["data-days"]
            )
            hours = ""
            for hour in hours_json:
                day = hour["day"]
                if len(hour["intervals"]) == 0:
                    hours += day + " Closed"
                    continue
                ints = hour["intervals"][0]
                start = ints["start"]
                end = ints["end"]
                hours += day + " " + str(start) + "-" + str(end) + " "

            hours = hours.strip()
            if hours == "":
                hours = "<MISSING>"

            street_address = loc.find(
                "span", {"class": "c-address-street"}
            ).text.strip()

            city = (
                loc.find("span", {"class": "c-address-city"})
                .text.replace(",", "")
                .strip()
            )
            state = loc.find("abbr", {"class": "c-address-state"}).text
            zip_code = loc.find("span", {"class": "c-address-postal-code"}).text.strip()

            phone_number = loc.find("span", {"class": "c-phone-number-span"}).text

            store_number = "<MISSING>"
            location_type = name_brand.replace("  ", " ").strip()
            lat = "<MISSING>"
            longit = "<MISSING>"
            page_url = city_link

            country_code = "US"
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

    for link in link_list:
        if "../" in link:
            link = link.replace("../", base_url)
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        name_brand = soup.find("span", {"class": "location-name-brand"}).text.strip()
        name_loc = soup.find("span", {"class": "location-name-geo"}).text.strip()
        location_name = (name_brand + " " + name_loc).replace("  ", " ").strip()

        hours_json = json.loads(
            soup.find("div", {"class": "js-location-hours"})["data-days"]
        )
        hours = ""
        for hour in hours_json:
            day = hour["day"]
            if len(hour["intervals"]) == 0:
                hours += day + " Closed"
                continue
            ints = hour["intervals"][0]
            start = ints["start"]
            end = ints["end"]
            hours += day + " " + str(start) + "-" + str(end) + " "

        hours = hours.strip()

        street_address = soup.find("span", {"class": "c-address-street"}).text.strip()

        city = (
            soup.find("span", {"class": "c-address-city"}).text.replace(",", "").strip()
        )
        state = soup.find("abbr", {"class": "c-address-state"}).text
        zip_code = soup.find("span", {"class": "c-address-postal-code"}).text.strip()

        phone_number = soup.find("span", {"class": "c-phone-number-span"}).text

        store_number = "<MISSING>"
        location_type = name_brand.replace("  ", " ").strip()
        lat = soup.find("meta", {"itemprop": "latitude"})["content"]
        longit = soup.find("meta", {"itemprop": "longitude"})["content"]
        page_url = link
        country_code = "US"
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

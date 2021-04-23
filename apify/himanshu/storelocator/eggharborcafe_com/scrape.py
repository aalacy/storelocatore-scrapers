import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("eggharborcafe_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    url = "https://eggharborcafe.com/locations/"

    response = session.get(url, headers=headers)
    map_headers = {
        "authority": "eggharborcafe.com",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    map_res = session.get(
        "https://eggharborcafe.com/wp-json/wpgmza/v1/features/",
        headers=map_headers,
    )
    map_data = json.loads(map_res.text)["markers"]
    soup = BeautifulSoup(response.text, "lxml")
    for link in soup.find_all("a", text=re.compile("view location")):
        r_loc = session.get(link["href"], headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        location_name = (
            link["href"].split("/")[-2].capitalize().replace("-", " ").strip()
        )
        address = " ".join(
            list(soup_loc.find("div", {"id": "location_address"}).stripped_strings)
        ).split(",")
        street_address = " ".join(address[:-2]).strip()
        city = address[-2].strip()
        state = address[-1].split()[0].strip()
        zipp = address[-1].split()[-1].strip()
        phone = soup_loc.find("p", {"id": "location_phone"}).text.strip()
        hours_of_operation = (
            " ".join(
                list(soup_loc.find("p", {"id": "location_hours"}).stripped_strings)
            )
            .replace("Hours:", "")
            .strip()
        )
        
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        for mp in map_data:
            if len(mp["title"]) > 0:
                temp_loc = None
                if " " in location_name:
                    temp_loc = location_name.split(" ")[0].strip()
                else:
                    temp_loc = location_name

                if "Egg Harbor Cafe - " + temp_loc.capitalize() in mp["title"]:
                    latitude = mp["lat"]
                    longitude = mp["lng"]
                    break

        page_url = link["href"]

        store = []
        store.append("https://www.eggharborcafe.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

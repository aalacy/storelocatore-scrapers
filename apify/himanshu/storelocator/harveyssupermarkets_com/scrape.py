import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import datetime
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("harveyssupermarkets_com")
session = SgRequests()
now = datetime.datetime.today().strftime("%A")


def write_output(data):
    with open("harvery.csv", mode="w", encoding="utf-8") as output_file:
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
    addresess = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.harveyssupermarkets.com",
        "Referer": "https://www.harveyssupermarkets.com/Locator",
    }
    r = session.get("https://www.harveyssupermarkets.com/Locator", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    info = soup.find_all("a", {"class": "details-link"})
    for i in info:
        page_url = "https://www.harveyssupermarkets.com" + str(i["href"])
        soup1 = BeautifulSoup(session.get(page_url, headers=headers).text, "lxml")
        location_name = soup1.find("h1", {"class": "store_head"}).text.strip()
        addr = list(soup1.find_all("a", {"role": "link"})[0].stripped_strings)
        street_address = addr[0].strip(",")
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[1].strip().split(" ")[0]
        zipp = addr[1].split(",")[1].strip().split(" ")[1]
        store_number = (
            soup1.find("h2", {"class": "store_head m-left0"})
            .text.split("#")[1]
            .split("Store")[0]
            .strip()
        )
        phone = soup1.find("label", {"class": "mob_num"}).text.strip()
        latitude = (
            str(soup1).split("var locations  = [")[1].split("];")[0].split(",")[-3]
        )
        longitude = (
            str(soup1).split("var locations  = [")[1].split("];")[0].split(",")[-2]
        )
        hours_of_operation = " ".join(
            list(
                soup1.find(
                    "div", {"class": "dis-inflex stores_head Mdis-blk w-100"}
                ).stripped_strings
            )[1:]
        ).replace("Today", now)

        store = []
        store.append("https://www.harveyssupermarkets.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("Harveys Supermarket")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addresess:
            continue
        addresess.append(store[2])
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = "".join(
                    (
                        c
                        for c in unicodedata.normalize("NFD", store[i])
                        if unicodedata.category(c) != "Mn"
                    )
                )
                store[i] = store[i].replace(" ", " ")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

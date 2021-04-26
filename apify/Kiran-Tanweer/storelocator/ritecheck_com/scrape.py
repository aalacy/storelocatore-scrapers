from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ritecheck_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        temp_list = []
        for row in data:
            comp_list = [
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)
        logger.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    data = []
    i = 0
    j = 0
    stores = []
    location = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    search_url = "https://ritecheck.com/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locs = soup.findAll("div", {"class": "city-loc"})
    while i < len(locs):
        all_loc = locs[i].text
        locations = all_loc.replace("â", "-")
        locations = re.sub(pattern, ";", locations)
        locations = re.sub(cleanr, ";", locations)
        if i == 1:
            locations = locations.split("Monday")
            for loc in locations:
                loc = "Monday" + " " + loc
                stores.append(loc)
        else:
            stores.append(locs[i])
        i = i + 1
    stores.pop(1)

    while j < len(stores):
        if isinstance(stores[j], str):
            store = stores[j]
        else:
            store = stores[j].text
        store = store.replace("â", "-")
        store = re.sub(pattern, ";", store)
        store = re.sub(cleanr, ";", store)
        store = store.replace("\n", ";")
        store = store.split(";")

        if store[0] == "":
            store.pop(0)
        if store[-1] == "":
            store.pop(-1)
        if store[0] == "Monday":
            store.pop(0)
            store[0] = store[0].replace("- Wednesday", "Monday - Wednesday")
        if len(store) == 5:
            hours = store[0] + " " + store[1] + " " + store[2]
            addr = store[3]
            location.append(hours)
            location.append(addr)
        elif len(store) == 6:
            hours = store[0] + " " + store[1] + " " + store[2] + " " + store[3]
            addr = store[4]
            location.append(hours)
            location.append(addr)
        elif len(store) == 7:
            hours = store[0] + " " + store[1] + " " + store[2]
            addr1 = store[3]
            addr2 = store[4]
            addr3 = store[5]
            location.append(hours)
            location.append(addr1)
            location.append(hours)
            location.append(addr2)
            location.append(hours)
            location.append(addr3)
        elif len(store) == 8:
            if store[0] == "- Thursday 8 AM - 6 PM":
                store[0] = "Monday - Thursday 8 AM - 6 PM"
            hours = store[0] + " " + store[1] + " " + store[2] + " " + store[3]
            addr1 = store[4]
            addr2 = store[5]
            addr3 = store[6]
            location.append(hours)
            location.append(addr1)
            location.append(hours)
            location.append(addr2)
            location.append(hours)
            location.append(addr3)
        else:
            if store[0] == "- Friday 9 AM - 6 PM,":
                store[0] = "Monday - Friday 9 AM - 6 PM,"
            hours = store[0] + " " + store[1]
            addr1 = store[2]
            location.append(hours)
            location.append(addr1)
        j = j + 1
    h = 0
    while h < len(location):
        if (h % 2) == 0:
            hours = location[h].strip()
            address = location[h + 1].strip()
        data.append(
            [
                "https://ritecheck.com/",
                "https://ritecheck.com/",
                "<MISSING>",
                address,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "US",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )
        h = h + 1
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

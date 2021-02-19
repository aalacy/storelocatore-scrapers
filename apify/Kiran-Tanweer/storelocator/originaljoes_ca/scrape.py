from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("originaljoes_ca")

session = SgRequests()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "originaljoes.ca",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    state_list = [
        "Alberta",
        "British+Columbia",
        "Manitoba",
        "New+Brunswick",
        "Newfoundland+and+Labrador",
        "Northwest+Territories",
        "Nova+Scotia",
        "Nunavut",
        "Prince+Edward+Island",
        "Quebec",
        "Saskatchewan",
        "Yukon",
    ]
    for state in state_list:
        url = "https://originaljoes.ca/?citySearch=" + state
        stores_req = session.get(url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        soup = str(soup)
        locations = soup.split("var ojlocations = {")[1].split(
            "var currentLocation = {"
        )[0]
        locations = locations.split('"2"')[1]
        locations = locations.split('"holidayHours": {')
        locations.pop()
        for loc in locations:
            city = loc.split('"city": "')[1].split('",')[0].strip()
            state = loc.split('"province": "')[1].split('",')[0].strip()
            street = loc.split('"streetAddress": "')[1].split('",')[0].strip()
            pcode = loc.split('"postalCode": "')[1].split('",')[0].strip()
            phone = loc.split('"telephone": "')[1].split('",')[0].strip()
            coords = loc.split('"geo": "')[1].split('",')[0].strip()
            title = loc.split('"Title": "')[1].split('",')[0].strip()
            hours = loc.split('"hours": {')[1].split('"":""')[0].strip()
            hours = hours.replace('"', "")
            hours = hours.replace("\n", "")
            hours = re.sub(pattern, " ", hours)
            hours = re.sub(cleanr, " ", hours)
            hours = hours.strip()
            hours = hours.rstrip(",")
            coords = coords.split(",")
            lat = coords[0]
            lng = coords[1]
            street = street.replace("&#039;", "'")
            title = title.replace("&#039;", "'")
            link = "https://originaljoes.ca/home/" + title
            link = link.replace(" ", "-")
            if hours == "CLOSED FOR : RENOVATIONS":
                hours = "TEMPORARILY CLOSED"
            if hours == "TEMPORARILY: CLOSED":
                hours = "TEMPORARILY CLOSED"
            if hours == "TEMPORARILY : CLOSED":
                hours = "TEMPORARILY CLOSED"
            if (
                hours
                == "MON-SUN: ., Dine-In, Takeout & Delivery:: 11AM-10PM, Delivery Only: : 10PM-11PM"
            ):
                hours = "MON-SUN: 11AM-10PM"
            hours = hours.replace("., Dine-In, Takeout & Delivery:: ", "")

            data.append(
                [
                    "https://originaljoes.ca/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "CAN",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    lng,
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

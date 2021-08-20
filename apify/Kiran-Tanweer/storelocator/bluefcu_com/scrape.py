from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("bluefcu_com")

session = SgRequests()


headers = {
    "authority": "www.bluefcu.com",
    "method": "POST",
    "path": "/api",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "authorization": "Bearer",
    "content-length": "568",
    "content-type": "application/json;charset=UTF-8",
    "cookie": "__cfduid=dda80f6c82a4dd02fae9a98be176b61591614863508; _6c2bf=https://172.17.0.4:443; _ga=GA1.2.1126236999.1614863531; _gid=GA1.2.983958741.1614863531; _dc_gtm_UA-22110146-1=1; _fbp=fb.1.1614863537789.226611464",
    "origin": "https://www.bluefcu.com",
    "referer": "https://www.bluefcu.com/locations",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}
headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.bluefcu.com/api"
    payload = {
        "query": "\n  query($section:[String],$orderBy:String) {\n    entries(\n      section: $section\n      orderBy: $orderBy\n    ) \n    {\n      ... on locations_locations_Entry {\n        id\n        title\n        uri\n        url\n        address1\n        address2\n        city\n        state\n        zipCode\n        phoneNumber\n        map {\n          lat,\n          lng,\n          distance\n          parts {\n            state\n          }\n        }\n      }\n    }\n\n  }\n",
        "variables": {
            "section": "locations",
            "orderBy": "state ASC, city ASC, title ASC",
        },
    }
    req = session.post(url, headers=headers, json=payload).json()
    for locs in req["data"]["entries"]:
        storeid = locs["id"]
        title = locs["title"]
        link = locs["url"]
        street = locs["address1"]
        street2 = locs["address2"]
        city = locs["city"]
        state = locs["state"]
        pcode = locs["zipCode"]
        phone = locs["phoneNumber"]
        lat = locs["map"]["lat"]
        lng = locs["map"]["lng"]
        if street2 is not None:
            street = street + " " + street2
        r = session.get(link, headers=headers2)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.find("div", {"class": "block-accordion"})
            .find("div", {"class": "accordion-content"})
            .text
        )
        hours = re.sub(pattern, " ", hours)
        hours = re.sub(cleanr, " ", hours)
        hours = hours.replace("\n", " ").strip()

        data.append(
            [
                "https://www.bluefcu.com/",
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

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ruthschris_com")


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []

    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
    }
    session.get("https://www.ruthschris.com/", headers=headers)
    base_url = "https://www.ruthschris.com/restaurant-locations/"
    r = session.get(base_url, headers=headers)
    if "utils.restaurants" in r.text:
        json_data = json.loads(
            r.text.split("utils.restaurants =")[1]
            .split("locationsMap.init()")[0]
            .replace("];", "]")
        )
        for k in json_data:
            if k["AlertTitle"] == "Permanently Closed":
                continue

            location_type = "<MISSING>"
            if k["AlertTitle"] == "Temporarily Closed":
                location_type = "Temporarily Closed"

            location_name = k["Name"]
            street_address = k["Address1"] + " " + k["Address2"]
            city = (
                k["City"]
                .replace("Toronto, ON", "Toronto")
                .replace("Markham, ON", "Markham")
                .replace("Washington D.C.", "Washington")
                .replace("Ontario", "<MISSING>")
            )
            state = k["State"]
            if "970 Dixon Road " in street_address:
                state = "ON"
            if "9990 Jasper Ave" in street_address:
                state = "AB"
            if "Value" in k["CountryCode"]:
                country_code1 = k["CountryCode"]["Value"]
            else:
                country_code1 = "<MISSING>"
            zipp1 = k["Zip"]

            ca_zip_list = re.findall(
                r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}", str(zipp1)
            )
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"
            us_zip_list = re.findall(
                re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp1)
            )
            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            if "Calgary, Alberta" in location_name:
                zipp = "T2G OP5"
            if "T2G OP5" in zipp:
                country_code = "CA"
            if "L6G 0E6" in zipp:
                state = "ON"
            if "L2G 3V9" in zipp:
                state = "ON"
            phone = k["Phone"].replace("\t", "")
            latitude = k["Latitude"]
            longitude = k["Longitude"]
            page_url = k["Url"]
            logger.info(page_url)
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            b = soup1.find("div", {"class": "container hours"})
            if b is not None and b != []:
                m = list(b.stripped_strings)
                hours_of_operation = " ".join(m)
            else:
                hours_of_operation = "<MISSING>"
            store = []
            store.append("https://www.ruthschris.com")
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type)
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            if "Aruba" in country_code1:
                continue
            if "Panama" in country_code1:
                continue
            if "Mexico" in country_code1:
                continue
            if "Singapore" in country_code1:
                continue
            if "China" in country_code1:
                continue
            if "Indonesia" in country_code1:
                continue
            if "Japan" in country_code1:
                continue
            if "Taiwan" in country_code1:
                continue
            if "Hong Kong" in country_code1:
                continue
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

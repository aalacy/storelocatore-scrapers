from bs4 import BeautifulSoup
import csv
import time
import re
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("shopbedmart_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
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


locations = [
    "https://www.shopbedmart.com/hi/locations/",
    "https://www.shopbedmart.com/nw/locations/",
]


def fetch_data():
    data = []
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    for link in locations:
        url = link
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divloc = soup.find("div", {"class": "row location-list"})
        locs = divloc.findAll("div", {"class": "location-card"})
        for loc in locs:
            title = loc.find("h4", {"class": "location-card-title"}).find("a")
            link = title["href"].strip()
            title = title.text.strip()
            info = loc.find("p", {"class": "location-card-content"}).text
            info = re.sub(pattern, " ", info)
            info = re.sub(cleanr, " ", info)
            info = info.split("\n")
            if len(info) == 5:
                address = info[0]
                phone = info[1]
                hours = info[2]
            if len(info) == 4:
                address = info[0]
                phone = info[1]
                hours = info[2] + " " + info[3]
            if len(info) == 7:
                address = info[0]
                phone = info[1]
                hours = info[2] + " " + info[3] + " " + info[4]
            if len(info) == 6:
                address = info[0]
                phone = info[1]
                hours = info[3]
            if address == " 1825 Haleukana St Unit C, Lihue 808-600-3934":
                address = " 1825 Haleukana St Unit C, Lihue"
                phone = "808-600-3934"
                hours = info[1]
            if address == " 380 Dairy Rd Kahului, HI 808.376.2740":
                address = " 380 Dairy Rd Kahului, HI"
                phone = "808.376.2740"
                hours = info[1] + " " + info[2] + " " + info[3]
            if address == " 1039 NW Glisan St Portland, OR 97209":
                hours = info[2] + " " + info[3]
            if address == " 15387 bangy road lake oswego, or 503.639.9750":
                address = " 15387 bangy road lake oswego, or"
                phone = "503.639.9750"
                hours = info[1] + " " + info[2] + " " + info[3]
            address = address.strip()
            phone = phone.strip()
            hours = hours.strip()

            title = title.rstrip(" – Pickup Only")
            hours = hours.rstrip(" Directions")

            address = address.replace(",", " ")
            address = usaddress.parse(address)

            i = 0
            street = ""
            city = ""
            state = ""
            pcode = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street = street + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                i += 1
            street = street.lstrip()
            street = street.replace(",", "")
            city = city.lstrip()
            city = city.replace(",", "")
            state = state.lstrip()
            state = state.replace(",", "")
            pcode = pcode.lstrip()
            pcode = pcode.replace(",", "")

            if pcode == "":
                pcode = "<MISSING>"
            if street == "1825 Haleukana St Unit C Lihue":
                street = "1825 Haleukana St Unit C"
                city = "Lihue"
                state = "HI"
                pcode = "<MISSING>"
            if state == "or":
                state = "OR"
            if state == "hi":
                state = "HI"
            p = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(p.text, "html.parser")

            scripts = soup.findAll("script")
            script = str(scripts[29])
            coords = script.split("center: {")[1].split("},")[0]
            coords = coords.split(",")
            lat = coords[0].strip()
            lat = lat.split("lat: ")[1]
            lng = coords[1].strip()
            lng = lng.split("lng: ")[1]

            if street == "15387 bangy road lake":
                street = "15387 bangy road"
                city = "lake oswego"
            data.append(
                [
                    "https://www.shopbedmart.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
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

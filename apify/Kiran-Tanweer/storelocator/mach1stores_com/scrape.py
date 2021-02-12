import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup
from bs4 import BeautifulSoup


logger = SgLogSetup().get_logger("mach1stores_com")

session = SgRequests()
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Length": "26",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "_ga=GA1.2.1628671476.1612123748; exp_last_visit=1612305902; exp_csrf_token=81c58a280e1428ab2ce7f0df1e42e3f620e4add6; _gid=GA1.2.74361419.1612467918; exp_tracker=%7B%220%22%3A%22locations%22%2C%221%22%3A%22locations%2Fstore-1%22%2C%222%22%3A%22locations%22%2C%223%22%3A%22locations-all%22%2C%22token%22%3A%22f5ae02c3a297472aab4800df9b724e6b1225aeaf02fd9c28749dfce36d66bd0709e9a8ef26299f87621eaff62a94b64a%22%7D; exp_last_activity=1612468900",
    "Host": "mach1stores.com",
    "Origin": "https://mach1stores.com",
    "Referer": "https://mach1stores.com/locations",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

form_data = {
    "cat": "",
    "count": "0",
    "keyword": "",
}

headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
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
        temp_list = []  # ignoring duplicates
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
    url = "https://mach1stores.com/__locations.php"
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    r = session.post(url, headers=headers, data=form_data, verify=False).json()
    for loc in r:
        address = loc["field_id_31"]
        title = loc["title"]
        lat = loc["field_id_46"]
        lng = loc["field_id_45"]
        url_title = loc["url_title"]
        link = "https://mach1stores.com/locations/" + url_title
        storeid = url_title
        storeid = storeid.lstrip("store-")
        p = session.get(link, headers=headers2, verify=False)
        soups = BeautifulSoup(p.text, "html.parser")
        time = soups.find("div", {"class": "results"})
        if len(time) == 5:
            hours = time.findAll("p")[1].text.strip()
        if len(time) == 3:
            hours = "<MISSING>"
            hours = hours.strip()
        if len(time) == 7:
            t = time.findAll("p")
            hours = t[1].text + " " + t[2].text
            hours = hours.strip()
        if hours == "":
            hours = "<MISSING>"
        address = address.replace("<br />", "")
        address = address.replace("<p>", "")
        address = address.replace("</p>", "")
        address = address.strip()
        address = re.sub(pattern, " ", address)
        address = re.sub(cleanr, " ", address)
        address = address.replace("&nbsp;", "")
        address = address.strip()
        address = address.split("\n")
        if len(address) != 1:
            phone = address[-1].strip()
            phone = phone.lstrip("Phone: ")
            address = address[0] + " " + address[1]
            address = address.replace("&nbsp;", " ")
        else:
            if address[0] != "":
                address = address[0].strip()
                phone = address.split(" ")[-1]
            else:
                address = address[0]

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

        if phone == "":
            phone = "<MISSING>"

        if street == "709 W. Main St. 618-663-4894":
            street = "709 W. Main St."

        if title != "Mach 21 Liquor Store":

            data.append(
                [
                    "https://mach1stores.com/",
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

from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("alaskacommercial_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
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
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.alaskacommercial.com/store-locator"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    scripts = soup.findAll("script")[8]
    scripts = str(scripts)
    scripts = scripts.split("},{")
    for loc in scripts:
        loc = re.sub(pattern, " ", loc)
        loc = re.sub(cleanr, " ", loc)
        storeid = loc.split('"pid":"')[1].split('"')[0]
        title = loc.split('"title":"')[1].split('"')[0]
        lat = loc.split('"lat":"')[1].split('"')[0]
        lng = loc.split('"lng":"')[1].split('"')[0]
        info = soup.find("div", {"data-id": storeid})
        address = info.find("p", {"class": "address"}).text
        address = re.sub(pattern, " ", address)
        address = re.sub(cleanr, " ", address)
        address = address.split("\n")
        addr = address[0]
        phone = address[1]
        phone = phone.lstrip("Phone: ")
        if phone.find("Fax:") != -1:
            phone = phone.split("Fax:")[0]
        phone = phone.strip()
        address = addr
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

        if storeid == "133":
            street = "Mile 1 Teller Hwy"
            city = "Nome"
        if storeid == "122":
            street = "155 Main St."
            city = "Fort Yukon"
        if storeid == "112":
            street = "229 Pisokak St. Utqiagvik, Alaska"
            city = "Utqiagvik"

        data.append(
            [
                "https://www.alaskacommercial.com/",
                "https://www.alaskacommercial.com/store-locator",
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
                "<MISSING>",
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

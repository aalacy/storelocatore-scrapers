from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress
import requests

logger = SgLogSetup().get_logger("officetaverngrill_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    data = []
    url = "http://www.officetaverngrill.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll(
        "li",
        id=lambda value: value
        and value.startswith("ctl01_ucMenuItems_rptHeaderMenu_ctl00"),
    )

    for div in divlist:
        link = div.find("a")["href"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.text.split("|", 1)[0]
        phone = soup.text.split("PHONE", 1)[1].split("Less", 1)[0].split(": (", 1)[0]
        phone = phone.replace("(", "").replace(")", "").replace(":", "")
        phone = phone.lstrip()
        address = soup.text.split("ADDRESS:", 1)[1].split("Less", 1)[0]
        googlelink = soup.findAll("span", {"class": "underline ai-rf"})
        for g in googlelink:
            if "maps" in g.find("a").get("href"):
                googlel = g.find("a").get("href")
                break
        try:
            googlel = requests.head(googlel, allow_redirects=True).url
        except:
            googlel = requests.head(googlel, allow_redirects=True).url
        lat = googlel.split("@", 1)[1].split(",")[0]
        long = googlel.split("@", 1)[1].split(",")[1]

        address = address.strip()
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

        hours = soup.text.split("Hours", 1)[1].split("The", 1)[0].split("ours", 1)[1]
        hours = hours.replace("AM", "AM ").replace("  ", " ")

        try:
            hours = hours.split("Less", 1)[0]
        except:
            pass
        data.append(
            [
                "http://www.officetaverngrill.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",  # store
                phone,
                "<MISSING>",
                lat,
                long,
                hours.replace("\n", " "),
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

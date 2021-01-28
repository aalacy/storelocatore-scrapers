from bs4 import BeautifulSoup
import csv
import re
import json
import usaddress

from sgrequests import SgRequests

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
    p = 0
    data = []
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.toniguy.com/find-salon/"
    r = session.get(url, headers=headers, verify=False)
    loclist = r.text.split(',"salons_data":"', 1)[1].split(']"', 1)[0]
    loclist = loclist.replace("\\n", "").replace("\\", "") + "]"
    loclist = json.loads(loclist)
    for loc in loclist:
        link = loc["url"]
        address = loc["address"]
        address = BeautifulSoup(address, "html.parser")
        address1 = re.sub(cleanr, " ", str(address)).strip()
        address = usaddress.parse(address1)
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
                or temp[1].find("Occupancy") != -1
                or temp[1].find("Recipient") != -1
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
        street = street.lstrip().replace(",", "")
        city = city.lstrip().replace(",", "")
        state = state.lstrip().replace(",", "")
        pcode = pcode.lstrip().replace(",", "")
        lat = loc["lat"]
        longt = loc["lng"]
        title = loc["title"]
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        phone = soup.find("a", {"class": "phone"}).text
        hours = (
            soup.find("div", {"class": "schedule"})
            .find("ul")
            .text.strip()
            .replace("M", "M ")
            .replace("T", "T ")
            .replace("W", "W ")
            .replace("F", "F ")
            .replace("S", "S ")
        )
        ccode = "US"
        if len(city) < 2 and len(pcode) < 2:
            address = loc["address"]
            address = BeautifulSoup(address, "html.parser")
            address = re.sub(cleanr, "\n", str(address)).strip().splitlines()
            street = address[0]
            city, state = address[1].split(", ", 1)
            state, pcode = state.lstrip().split(" ", 1)
            ccode = "CA"
        data.append(
            [
                "https://www.toniguy.com/",
                link,
                title,
                street,
                city,
                state.replace(".", "").upper(),
                pcode.replace(".", ""),
                ccode,
                "<MISSING>",
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

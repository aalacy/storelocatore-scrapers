from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("credobeauty_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
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
    url = "https://credobeauty.com/blogs/credo-stores"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loc_div = soup.find("div", {"class": "sixteen columns store-row"})
    loc = loc_div.findAll("div", {"class": "one-third"})
    for info in loc:
        address = info.find("div", {"class": "address-store"})
        addr = address.text
        ptag = address.findAll("p")
        if len(ptag) > 1:
            lat = "<MISSING>"
            longt = "<MISSING>"
            coord_link = "<MISSING>"
        else:
            coord = info.find("a", {"class": "sign_up_btn"})
            if coord is not None:
                coord_link = coord["href"]
                points = coord_link.split("/@")[1].split(",")
                lat = points[0]
                longt = points[1]
            else:
                if addr == " 552 Hayes StreetSan Francisco, CA 94102":
                    lat = "<MISSING>"
                    longt = "<MISSING>"
                    coord_link = "<MISSING>"
                if (
                    addr == " 1659 N Damen AveChicago, IL 60647"
                    or addr == " 9 Prince Street New York, NY 10012"
                ):
                    coord_link = ptag[0].find("a")["href"]
                    points = coord_link.split("/@")[1].split(",")
                    lat = points[0]
                    longt = points[1]
                if addr == " 99 N. 6th St.Brooklyn, NY 11249":
                    coord_link = ptag[0].findAll("a")[0]
                    coord_link = coord_link["href"]
                    points = coord_link.split("/@")[1].split(",")
                    lat = points[0]
                    longt = points[1]

        atags = info.findAll("a")
        tag1 = atags[0]
        loclink = tag1["href"]
        phone = atags[-1].text
        loclink = "https://credobeauty.com" + loclink
        p = session.get(loclink, headers=headers, verify=False)
        soup = BeautifulSoup(p.text, "html.parser")
        location = soup.find("div", {"class": "location__content"})
        title = location.find("h2").text.strip()
        addr = addr.strip()
        addr = addr.replace("\n", " ")
        addr = addr.lstrip("The Shops At Legacy West")
        if addr.find("Street") != -1:
            addr = addr.replace("Street", "Street ")
        if addr.find("Damen Ave") != -1:
            addr = addr.replace("Ave", "Ave ")
        if addr.find("G160") != -1:
            addr = addr.replace("G160", "G160 ")
        if addr.find("Street  New York") != -1:
            addr = addr.replace("Street  New York", "Street New York")
        addr = addr.replace(",", "")
        address = usaddress.parse(addr)
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

        hours = soup.find("div", {"class": "store-hours"}).text
        hours = re.sub(pattern, " ", hours).strip()
        hours = hours.split("Store Hours ")[1].split(" SPECIAL")[0]

        data.append(
            [
                "https://credobeauty.com/",
                loclink,
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
                longt,
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

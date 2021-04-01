from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("elizabethgrady_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    url = "https://www.elizabethgrady.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "et_pb_row locations-row"})
    for loc in loclist:
        all_div = loc.findAll("div")
        title = all_div[0].find("h3").text
        phone = all_div[1].find("a")
        if phone is None:
            phone = all_div[1]
            phone = str(phone)
            phone = re.sub(pattern, " ", phone)
            phone = re.sub(cleanr, " ", phone)
            phone = phone.split("   ")[1].split("   Now Open!")[0]
        else:
            phone = phone.text
        addr = all_div[1]
        addr = str(addr)
        addr = addr.split('">')[1].split("<a href")[0]
        addr = addr.replace("<br/>", " ").strip()
        hours = all_div[-1].text
        hours = re.sub(pattern, " ", hours)
        hours = re.sub(cleanr, " ", hours)

        address = addr.replace(",", " ")
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

        if (
            street
            == '104 Spit Brook Road Suite A 603-943-5531 div class="special-message'
        ):
            street = "104 Spit Brook Road Suite A"

        if street == '45 Lafayette Road 603-964-9492 div class="special-message':
            street = "45 Lafayette Road"

        if street == '240 North Broadway 603-893-3535 div class="special-message':
            street = "240 North Broadway"

        data.append(
            [
                "https://www.elizabethgrady.com/",
                "https://www.elizabethgrady.com/locations/",
                title,
                street,
                city,
                state,
                pcode,
                "US",
                "<MISSING>",
                phone,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
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

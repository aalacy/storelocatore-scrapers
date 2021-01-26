from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("emetabolic_com")

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
    pattern = re.compile(r"\s\s+")
    data = []
    for i in range(1, 52):
        p = str(i)
        url = "https://www.emetabolic.com/?maps_markers=" + p
        r = session.get(url, headers=headers, verify=False)
        response = r.text
        loclist = response.split('"markers":')[1].split("]}", 1)[0]
        loclist = loclist + "]"
        loclist = json.loads(loclist)
        if loclist:
            for loc in loclist:
                title = loc["name"].strip()
                lat = loc["lat"].strip()
                longt = loc["lng"]
                adrs = loc["address"]
                link_url = loc["link_url"]
                linkurl = link_url
                p = session.get(link_url, headers=headers, verify=False)
                soup = BeautifulSoup(p.text, "html.parser")
                div = soup.findAll("div", {"class": "location-contact-data"})
                if len(div) > 0:
                    add = div[0].text
                    add = re.sub(pattern, ",", add)
                    add = add.rstrip(" Get Directions,")
                    add = add.replace(",", "")
                    address = usaddress.parse(add)
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
                else:
                    adrs = adrs.split(",")
                    street = adrs[0].strip()
                    city = adrs[1].strip()
                    state = adrs[2].strip()
                    pcode = "<MISSING>"
                    linkurl = url
                div = soup.findAll("div", {"class": "location-contact-data"})
                if (len(div)) == 0:
                    phone = "<MISSING>"
                else:
                    phone = div[1].text
                    phone = phone.strip()
                time = soup.findAll("div", {"class": "location-hours-info"})
                HOO = ""
                for day in time:
                    hours = day.text
                    HOO = HOO + hours
                if HOO == "":
                    HOO = "<MISSING>"
                HOO = HOO.strip()

                if street == "15060 Sequoia Pkwy # 6Tigard":
                    street = "15060 Sequoia Pkwy # 6"
                    city = "Tigard"
                data.append(
                    [
                        "https://www.emetabolic.com/",
                        linkurl,
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
                        HOO,
                    ]
                )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

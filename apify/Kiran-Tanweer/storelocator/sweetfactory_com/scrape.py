from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress
import re

logger = SgLogSetup().get_logger("sweetfactory_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
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
    divs = []
    k = 0
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://www.sweetfactory.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    info1 = soup.find("div", {"id": "block-yui_3_17_2_1_1531863435161_12648"})
    divs.append(info1)
    info2 = soup.find("div", {"id": "block-yui_3_17_2_1_1532551192232_6671"})
    divs.append(info2)
    for locs in divs:
        locations = locs.findAll("p")
        for loc in locations:
            if k != 1 and k != 4:
                link = loc.find("a")["href"]
                addr = str(loc)
                title = addr.split("<strong>")[1].split("</strong>")[0]
                title = title.rstrip("*").strip()
                address = addr.split("</a><br/>")[1].split("<br/>Tel:")[0]
                address = address.replace("<br/>", " ")
                address = address.replace("   ", " ")
                phone = addr.split("Tel:")[1].split("</p>")[0].strip()
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
                r = session.get(link, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                hours = soup.findAll("tr")
                if len(hours) == 14:
                    hoo = ""
                    for h in range(0, len(hours)):
                        if h % 2 != 0:
                            hour = hours[h].text
                            hoo = hour + " " + hoo
                            hoo = hoo.strip()
                            hoo = hoo.replace("Closed now", "")
                            hoo = hoo.replace("Sun", "Sun ")
                            hoo = hoo.replace("Fri", "Fri ")
                            hoo = hoo.replace("Thu", "Thu ")
                            hoo = hoo.replace("Wed", "Wed ")
                            hoo = hoo.replace("Tue", "Tue ")
                            hoo = hoo.replace("Mon", "Mon ")
                            hoo = hoo.replace("Sat", "Sat ")
                            hoo = hoo.replace("Open now", "")
                            hoo = re.sub(pattern, " ", hoo)
                            hoo = re.sub(cleanr, " ", hoo)
                else:
                    hoo = "<MISSING>"
                data.append(
                    [
                        "https://www.sweetfactory.com/",
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
                        "<INACCESSIBLE>",
                        "<INACCESSIBLE>",
                        hoo,
                    ]
                )
            k = k + 1
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

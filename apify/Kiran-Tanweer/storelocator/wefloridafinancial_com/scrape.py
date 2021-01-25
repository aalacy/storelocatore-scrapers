from bs4 import BeautifulSoup
import csv
import time
import re
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress


logger = SgLogSetup().get_logger("wefloridafinancial_com")

session = SgRequests()
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "02074834db43263db4c81cf728ac8181=a7a37a1270df4ac8003fac5a09f66bf2; nrid=be07924d965fee03; _gcl_au=1.1.2124703621.1610474198; _ga=GA1.2.459863425.1610474200; _gid=GA1.2.1486209106.1610474200; _fbp=fb.1.1610474202584.161074790; pageviewCount=8",
    "Host": "www.wefloridafinancial.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.wefloridafinancial.com/locations"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    for i in range(1, 3):
        j = str(i)
        div = soup.findAll("div", {"id": "set-rl_sliders-" + j})
        for locs in div:
            loc = locs.findAll(
                "div",
                {"class": "accordion-group panel rl_sliders-group nn_sliders-group"},
            )
            for l in loc:
                title = l.find(
                    "span", {"class": "rl_sliders-toggle-inner nn_sliders-toggle-inner"}
                ).text
                info = l.findAll("div", {"class": "tableFloat"})
                address = info[0].find("a")
                coords = address["href"]
                if coords.find("www.google.com") != -1:
                    coords = coords.split("/@")[1].split(",17z")[0]
                    coords = coords.split(",")
                    lat = coords[0]
                    lng = coords[1]
                else:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                address = str(address)
                address = address.split('target="_blank">')[1].split("</a>")[0]
                address = address.replace("<br/>", " ")
                address = address.strip()
                address = address.replace(",", "")
                if address != "4300 Alton Road Ascher Building Miami Beach FL 33140":
                    hours = info[1].text
                    hours = hours.split("Drive-up Window Hours")[0]
                    hours = re.sub(pattern, " ", hours)
                    hours = re.sub(cleanr, " ", hours)
                    hours = hours.strip()
                    hours = hours.lstrip("Lobby Hours ")
                    hours = hours.lstrip(
                        "**Share Branching will remain Drive-Thru only** "
                    )
                    hours = hours.lstrip("Lobby Hours ")
                    hours = hours.lstrip("No Share Branching** Lobby Hours ")
                    hours = hours.replace("(by appointment only)", "")
                    hours = hours.replace("  ", " ")
                else:
                    hours = "<MISSING>"

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

                data.append(
                    [
                        "https://www.wefloridafinancial.com/",
                        "https://www.wefloridafinancial.com/locations",
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        "US",
                        "<MISSING>",
                        "<MISSING>",
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

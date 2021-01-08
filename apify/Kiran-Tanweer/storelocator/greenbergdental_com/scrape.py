from bs4 import BeautifulSoup
import csv
import re
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("greenbergdental_com")

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
    HOO = ""
    pattern = re.compile(r"\s\s+")
    url = "https://www.greenbergdental.com/map/#all"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    office_div = soup.find("div", {"class": "office-list"})
    lists = office_div.find("ul", {"class": "list"})
    office_list = lists.findAll("li")
    for li in office_list:
        add = li["data-address"]
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
        lat = li["data-lat"]
        longt = li["data-lng"]
        info = li.find("a")
        page_link = info["href"]
        title = info.text
        p = session.get(page_link, headers=headers, verify=False)
        soup = BeautifulSoup(p.text, "html.parser")
        info2 = soup.find("div", {"id": "office-info"})
        phone = info2.find("p", {"class": "tel"}).text.lstrip("Call: ")
        hours = soup.find("div", {"class": "hours"})
        if city == "Richey":
            city = "Port Richey"
            street = "8631 US-19"
        if hours is None:
            hrs = "Coming soon"
        else:
            schedule = hours.findAll("span")
            for hour in schedule:
                time = hour.text.strip()
                time = re.sub(pattern, "\n", time)
                time = time.replace("\n", " ")
                HOO = HOO + time + ", "
            hrs = HOO.rstrip(", ")
            HOO = ""

        data.append(
            [
                "https://www.greenbergdental.com/",
                page_link,
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
                hrs,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

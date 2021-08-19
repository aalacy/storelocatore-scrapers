from bs4 import BeautifulSoup
import csv
import re
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress


logger = SgLogSetup().get_logger("giantfitnessclubs_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
    url = "https://giantfitnessclubs.com/locations/"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.findAll("div", {"class": "column_attr clearfix align_center"})
    for loc in locations:
        link = loc.find("a")["href"]
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        title = soup.find("h1", {"class": "title"}).text
        info = soup.findAll("div", {"class": "column_attr clearfix"})
        if title == "Giant Fitness – Voorhees NJ":
            info = info[1].text
            address = info.split("Phone:  ")[0]
            phone = info.split("Phone:  ")[1].split("\n")[0]
            hours = info.split("Gym Hours:")[1]
        if title == "Giant Fitness – Philadelphia PA":
            address = info[1]
            phone = info[2].text
            hours = info[3].text
        if title == "Giant Fitness – Mt Laurel NJ":
            address = info[1]
            phone = info[2].text
            hours = info[3].text
        if title == "Giant Fitness – Mount Ephraim NJ":
            address = info[-3]
            phone = info[-2].text
            hours = info[-1].text
        if title == "Giant Fitness – Woodbury Heights NJ":
            address = info[1]
            phone = info[2].text
            hours = info[3].text
        if title == "Giant Fitness – Washington Township NJ":
            address = info[2]
            phone = info[3].text
            hours = info[4].text
        if title == "Giant Fitness – Blackwood NJ":
            address = info[2]
            phone = info[3].text
            hours = info[4].text
        address = str(address)
        address = address.replace(
            '<div class="column_attr clearfix" style=""><b>Address:</b><br/>', ""
        )
        address = address.replace("<br/><br/></div>", "")
        address = address.replace(
            '<div class="column_attr clearfix" style=""><b>Address:</b>', ""
        )
        address = address.replace("Address:", "")
        address = address.replace("</div>", "")
        address = address.strip()
        address = address.replace(
            "120 Britton PlaceVoorhees, NJ 08043",
            "120 Britton Place Voorhees, NJ 08043",
        )
        address = address.replace("<br/>", " ")
        address = address.replace(",", "")
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
        phone = phone.lstrip("Phone: ").strip()

        hours = hours.replace("\n", " ")
        hours = hours.lstrip("Hours:")
        hours = re.sub(pattern, " ", hours)
        hours = re.sub(cleanr, " ", hours)
        hours = hours.strip()

        data.append(
            [
                "https://giantfitnessclubs.com/",
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

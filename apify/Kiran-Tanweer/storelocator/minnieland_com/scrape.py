from bs4 import BeautifulSoup
import csv
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("minnieland_com")

session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
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
    url = "https://www.minnieland.com/about-us/all-school-locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("div", {"class": "locationRow wrap"})
    for loc in locations:
        title = loc.find("h3").find("a")
        link = title["href"]
        title = title.text
        info = loc.findAll("div", {"class": "locationRowBox"})
        addr = info[0].text
        addr = addr.replace("Plaza", "Plaza ")
        addr = addr.replace("Street", "Street ")
        addr = addr.replace("Drive", "Drive ")
        addr = addr.replace("Boulevard", "Boulevard ")
        addr = addr.replace("Way", "Way ")
        addr = addr.replace("Pkwy", "Pkwy ")
        addr = addr.replace("Blvd", "Blvd ")
        addr = addr.replace("Place", "Place ")
        addr = addr.replace("Dale City", " Dale City")
        addr = addr.replace("Haymarket", " Haymarket")
        addr = addr.replace("Road", "Road ")
        addr = addr.replace("Parkway", "Parkway ")
        addr = addr.replace("Avenue", "Avenue ")
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

        street = street.strip()
        city = city.strip()
        state = state.strip()
        pcode = pcode.strip()

        phone = info[1].text.strip()
        hours = info[2].text.strip()
        hours = hours.replace("p.m.", "pm")
        hours = hours.replace("a.m.", "am")
        hours = hours.replace("pm", "pm,")
        hours = hours.split(",")[0].strip()

        p = session.get(link, headers=headers, verify=False)
        bs = BeautifulSoup(p.text, "html.parser")
        coords = bs.find("div", {"class": "schoolLocDiv"}).find("script")
        coords = str(coords)
        coords = coords.lstrip("<script>initSchoolMap(")
        coords = coords.rstrip(");</script>")
        if len(coords) == 1:
            lat = "<MISSING>"
            lng = "<MISSING>"
        else:
            coords = coords.split(",")
            lat = coords[0]
            lng = coords[1]

        data.append(
            [
                "https://www.minnieland.com/",
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

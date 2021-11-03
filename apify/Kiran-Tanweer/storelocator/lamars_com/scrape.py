from bs4 import BeautifulSoup
import csv
import time
import usaddress
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("lamars_com")

session = SgRequests()
headers = {
    "authority": "www.lamars.com",
    "method": "GET",
    "path": "/locations/",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "PHPSESSID=d3de290bb7d4636a0edbaae3d460d3f5; __utmc=261435152; __utmz=261435152.1612099515.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _fbp=fb.1.1612099516782.1235058980; __utma=261435152.1078465853.1612099515.1612099515.1612125096.2; __utmb=261435152.1.10.1612125096",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
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
    url = "https://www.lamars.com/locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    storelist = soup.findAll("td", {"class": "locationField"})
    for store in storelist:
        store1 = store
        title = store1.find("h3").text
        coords = store1.find("p").find("a")["href"]
        store = str(store)
        address = store.split("</strong>")[1].split("<strong>")[0]
        address = address.strip()
        if address == "":
            address = store.split("</strong><strong><br/>")[1].split("<strong>")[0]
        address = address.lstrip("</strong>")
        address = address.strip()
        address = address.strip("</strong>")
        address = address.replace("\n", "")
        address = address.lstrip('</span><br/><span style="color: #ff0000;">')
        address = address.replace("&amp;", "&")
        address = address.rstrip("<br/>")
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

        phone = store.split("hone:")[1].split("<br/>")[0]
        phone = phone.lstrip("</strong>").strip()
        phone = phone.lstrip("</strong>").strip()

        hours = store.split("Hours:")[1].split("<!")[0]
        hours = hours.replace("\n", " ")
        hours = hours.lstrip("</strong><br/>")
        hours = hours.lstrip("<br/>")
        hours = hours.rstrip("</strong>")
        hours = hours.replace("<br/>", " ")
        hours = hours.lstrip("</strong>")
        hours = hours.lstrip("</strong>")
        hours = hours.rstrip("<strong> </strong>")
        hours = hours.strip()
        hours = hours.replace("  ", "")
        hours = "00" + hours + "00"
        hours = hours.lstrip("00</strong>")
        hours = hours.rstrip("<strong> </strong>00")
        hours = hours.replace("Su", "Sun")
        if coords.find("/@") != -1:
            coord = coords.split("/@")[1].split(",17z")[0]
        if coord.find(",15z") != -1:
            coord = coord.split(",15z")[0]
        if coords.find("sll=") != -1:
            coord = coords.split("sll=")[1].split("&sspn")[0]

        centre = coord.split(",")
        lat = centre[0]
        lng = centre[1]

        data.append(
            [
                "https://www.lamars.com/",
                "https://www.lamars.com/locations/",
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

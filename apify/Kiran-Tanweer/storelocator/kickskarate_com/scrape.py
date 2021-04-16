from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape import sgpostal as parser


logger = SgLogSetup().get_logger("kickskarate_com")

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
    search_url = "https://kickskarate.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    links = soup.findAll("a", string=" Explore Location")
    for loc in links:
        url = loc["href"]
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        info = soup.find("div", {"class": "location"})
        title = info.find("h3", {"class": "white"}).text
        title = title.replace("\n", " ").strip()
        allp = info.findAll("p")
        address = allp[0].text
        address = address.split("\n")
        p = allp[0].text
        p = p.split("\n")
        if len(address) == 4:
            address = address[1] + " " + address[2] + " " + address[3]
        if len(address) == 3:
            address = address[1] + " " + address[2]
        if len(address) == 5:
            address = address[2] + " " + address[3] + " " + address[4]
        if len(address) == 8:
            address = address[2] + " " + address[3] + " " + address[4]
        phone = allp[1].find("a")["href"]
        parsed = parser.parse_address_usa(address)
        street1 = parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
        street = (
            (street1 + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street1
        )
        city = parsed.city if parsed.city else "<MISSING>"
        state = parsed.state if parsed.state else "<MISSING>"
        pcode = parsed.postcode if parsed.postcode else "<MISSING>"
        if phone.find("tel") == -1:
            phone = p[-3]
        phone = phone.lstrip("tel:").strip()
        coords = allp[1].findAll("a")[-1]
        coords = coords["href"]
        if coords.find("17z") != -1:
            lat, lng = coords.split("/@")[1].split(",17z/")[0].split(",")
        elif coords.find("75z") != -1:
            lat, lng = coords.split("/@")[1].split(",18.")[0].split(",")
        else:
            lat = "<MISSING>"
            lng = "<MISSING>"
        hours = soup.findAll("p")
        if len(hours) == 24:
            hours = soup.findAll("p")[1].text
        else:
            hours = soup.findAll("p")[2].text

        hoo = hours.replace("\n", " ")
        hoo = hoo.rstrip("Tell Me More").strip()

        data.append(
            [
                "https://kickskarate.com/",
                url,
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
                hoo,
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

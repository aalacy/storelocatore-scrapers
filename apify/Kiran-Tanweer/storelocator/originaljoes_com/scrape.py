from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("originaljoes_com")

session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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
    search_url = "https://originaljoes.com/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    loc_link = soup.findAll("a", {"class": "location-links"})
    for loc in loc_link:
        link = loc["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        footer = soup.find("div", {"class": "mkdf-container"}).findAll("p")
        address = footer[1].find("a")
        coords = address["href"]
        address = address.text.strip()
        address = address.split("\n")
        title = address[0].strip()
        street = address[1].strip()
        locality = address[2].strip()
        locality = locality.split(",")
        city = locality[0].strip()
        statezip = locality[1].strip()
        statezip = statezip.split(" ")
        state = statezip[0].strip()
        pcode = statezip[1].strip()
        coords = coords.split("@")[1].split(",17z")[0]
        coords = coords.split(",")
        lat = coords[0]
        lng = coords[1]
        phone = footer[2].findAll("a")[1].text
        hours = footer[3].text
        hours = hours.replace("\n", " ")
        hours = hours.replace("thru", "to")
        hours = hours.strip()
        phone = phone.strip()

        data.append(
            [
                "https://originaljoes.com/",
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

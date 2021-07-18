from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("seaboardwarehouse_com")

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
    search_url = "https://www.seaboardwarehouse.com/services/food-grade-storage/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.find("div", {"class": "sbrr"}).findAll("div", {"class": "sbru"})
    for loc in locations:
        title = loc.find("h5").text.strip()
        address = loc.find("div", {"class": "addr"}).text.strip()
        phone = address.split("Ph.")[1].strip()
        phone = phone.split("\n")[0].strip()
        address = address.split("Ph. ")[0].strip()

        if len(address.split("\n")) > 2:
            street = address.split("\n")[0] + " " + address.split("\n")[1]

        else:
            street = address.split("\n")[0]
        city = address.split("\n")[-1].split(", ")[0]
        state = address.split("\n")[-1].split(", ")[1].split(" ")[0]
        pcode = address.split("\n")[-1].split(", ")[1].split(" ")[1]

        coords = loc.find("a")["href"]
        coords = coords.split("C=")[1].split("&A")[0]
        lat, lng = coords.split(",")
        lat = lat.strip()
        lng = lng.strip()

        data.append(
            [
                "https://www.seaboardwarehouse.com/",
                search_url,
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
                "<MISSING>",
            ]
        )
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

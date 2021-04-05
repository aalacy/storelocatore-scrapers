from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("creativekidslearningcenter_com")

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
    search_url = "https://www.creativekidslearningcenter.com/locations/"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    divlist = soup.find("div", {"class": "locationCards thisBrand row"}).findAll(
        "div", {"class": "locationCard"}
    )
    for div in divlist:
        link = div.find("a", {"class": "schoolNameLink"})
        title = link.text
        link = "https://www.creativekidslearningcenter.com/" + link["href"]
        phone = div.find("p", {"class": "phone vcard"}).find("a").text
        hours = div.find("p", {"class": "hours"}).text
        address = div.find("span", {"class": "addr"})
        lat = address["data-latitude"]
        lng = address["data-longitude"]
        street = address.find("span", {"class": "street"}).text
        locality = address.find("span", {"class": "cityState"}).text
        city, locality = locality.split(",")
        locality = locality.strip()
        state, pcode = locality.split(" ")
        hours = hours.lstrip("Open:").strip()

        data.append(
            [
                "https://www.creativekidslearningcenter.com/",
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

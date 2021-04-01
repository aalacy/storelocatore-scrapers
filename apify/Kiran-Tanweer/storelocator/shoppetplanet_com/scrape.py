from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("shoppetplanet_com")

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
    url = "https://www.shoppetplanet.com/store-locations/"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locs = soup.findAll("li", {"class": "sl-region"})
    for loc in locs:
        loclink = loc.find("a")["href"]
        stores_req = session.get(loclink, headers=headers)
        s = BeautifulSoup(stores_req.text, "html.parser")
        links = s.findAll("a", {"class": "si-title"})
        for li in links:
            if loclink.find("/canada/") != -1:
                country = "CAN"
            else:
                country = "US"
            link = li["href"]
            r = session.get(link, headers=headers)
            bs = BeautifulSoup(r.text, "html.parser")
            title = bs.find("h1", {"class": "store-title"}).text
            address = bs.findAll("div", {"class": "addy1"})
            if len(address) == 4:
                street = address[0].text + " " + address[1].text
                locality = address[2].text
                pcode = address[3].text
            else:
                street = address[0].text
                locality = address[1].text
                pcode = address[2].text
            city, state = locality.split(",")
            city = city.strip()
            state = state.strip()
            phone = bs.find("p", {"class": "store-info"}).find("a").text
            hours = bs.find("p", {"class": "store-hours"}).text
            hours = hours.replace("\n", " ")
            hours = hours.split("Holidays :")[0].strip()
            data.append(
                [
                    "https://www.shoppetplanet.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    country,
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
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

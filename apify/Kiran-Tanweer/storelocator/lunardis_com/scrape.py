from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("lunardis_com")

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
    search_url = "https://www.lunardis.com/locations"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    divlist = soup.findAll("div", {"class": "bDfMI"})
    for div in divlist:
        details = div.text
        details = details.split("\n")
        hours = details[-1]
        if hours.find("Hours") != -1:
            hoo = details[-1]
            phone = details[-2]
        else:
            hoo = details[-2]
            phone = details[-3]
            if phone.find("Store Phone:") == -1:
                phone = details[-4]
        hoo = hoo.lstrip("Hours: Open Daily ").strip()
        hoo = hoo.replace("PEN DAILY ", "").strip()
        hoo = "Mon - Sun: " + hoo
        phone = phone.lstrip("Store Phone:").strip()
        title = div.findAll("div", {"class": "_3Mgpu"})[2]
        for t in title:
            allspan = t.findAll("span")
            title = allspan[0].text
            address = allspan[4].text + " " + allspan[5].text
            address = address.replace("\n", " ")
            address = address.split("Store Phone")[0].strip()
            street = address.replace("  ", "").strip()

            data.append(
                [
                    "https://www.lunardis.com/",
                    "https://www.lunardis.com/locations",
                    title,
                    street,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    "<INACCESSIBLE>",
                    "<INACCESSIBLE>",
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

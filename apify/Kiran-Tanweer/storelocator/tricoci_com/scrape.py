from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("tricoci_com")

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
    search_url = "https://www.tricoci.com/a/locations"
    stores_req = session.get(search_url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    links = soup.findAll("a", {"class": "Text--subdued Link Link--primary"})
    locs = soup.find("div", {"class": "addresses"}).findAll("a")
    i = 0
    while i < len(locs):
        loc = locs[i]
        title = loc.find("span", {"class": "name"}).text.strip()
        street = loc.find("span", {"class": "address"}).text.strip()
        city = loc.find("span", {"class": "city"}).text.strip()
        hours = loc.find("span", {"class": "hours"}).text
        link = loc.find("a", string="Details")["href"].strip()
        hours = hours.replace("pm", "pm ")
        hours = hours.replace("Closed", "Closed ")
        hours = hours.replace("DetailsBook Now", "")
        hours = hours.strip()
        r = session.get(link, headers=headers)
        bs = BeautifulSoup(r.text, "html.parser")
        info = bs.findAll("span")
        info = str(info[33])
        info = info.split(",")[1].strip()
        info = info.rstrip("</span>")
        info = info.split("<br/>")
        phone = info[1].strip()
        locality = info[0].strip().split(" ")
        state = locality[0].strip()
        pcode = locality[1].strip()

        data.append(
            [
                "https://www.tricoci.com/",
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
                "<MISSING>",
                "<MISSING>",
                hours,
            ]
        )
        i = i + 3
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

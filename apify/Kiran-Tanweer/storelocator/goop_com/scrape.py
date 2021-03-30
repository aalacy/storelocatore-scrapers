from bs4 import BeautifulSoup
import csv
import time
from sgrequests import SgRequests
from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("goop_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        temp_list = []  # ignoring duplicates
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
    url = "https://goop.com/goop-retail-store-locations/"
    r = session.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    locations = soup.findAll("div", {"class": "goop-retail-locations"})
    for loc in locations:
        title = loc.find("h3").text.strip()
        address = loc.find("p", {"class": "goop-retail-location-desc"}).text.strip()
        address = address.split("\n")
        street = address[0]
        csp = address[1]
        csp = csp.split(",")
        city = csp[0]
        sp = csp[1].strip()
        sp = sp.split(" ")
        state = sp[0].strip()
        pcode = sp[1].strip()
        phone = address[2]
        hours = loc.find("p", {"class": "goop-retail-location-hours"}).text.strip()
        if hours == "Closed until further notice":
            hours = "Closed"
        if hours.find("Daily") != -1:
            hours = hours.replace("Daily", "Monday-Sunday")
        hours = hours.replace("\n", " ").strip()

        data.append(
            [
                "https://goop.com/",
                "https://goop.com/goop-retail-store-locations/",
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
    return data


def scrape():
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))
    data = fetch_data()
    write_output(data)
    logger.info(time.strftime("%H:%M:%S", time.localtime(time.time())))


scrape()

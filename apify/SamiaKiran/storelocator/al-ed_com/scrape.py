import csv
import usaddress
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog

website = "al-ed_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    for x in range(1, 3):
        url = "https://al-ed.com/amlocator/index/ajax/?p=" + str(x)
        loclist = session.get(url, headers=headers).json()["items"]
        for loc in loclist:
            store = loc["id"]
            lat = loc["lat"]
            longt = loc["lng"]
            temp = loc["popup_html"]
            loc = BeautifulSoup(temp, "html.parser")
            ##            temp = (
            ##                soup.find("div", {"class": "amlocator-info-popup"})
            ##                .get_text(separator="|", strip=True)
            ##                .split("|")
            ##            )
            ##            temp = temp[:-3]
            ##            title = temp[0]
            ##            street = (
            ##                temp[1]
            ##                .split(
            ##                    ",",
            ##                )[0]
            ##                .split("Address: ")[1]
            ##            )
            ##            city = temp[3].split("City: ")[1]
            ##            state = temp[2].split("State: ")[1]
            ##            pcode = temp[4].split("Zip: ")[1]
            link = loc.find("a", {"class": "amlocator-link"})["href"]
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            address = soup.find("span", {"class": "amlocator-text -bold"}).text
            title = soup.find("h1").text
            phone = soup.find("div", {"class": "amlocator-block -contact"}).findAll(
                "div", {"class": "amlocator-block"}
            )
            phone = phone[1].find("a").text
            hour_list = soup.find("div", {"class": "amlocator-schedule-table"}).findAll(
                "div", {"class": "amlocator-row"}
            )
            hours = ""
            for hour in hour_list:
                hour = hour.findAll("span")[:-2]
                day = hour[0].text
                time = hour[1].text
                hours = hours + " " + day + " " + time
            hours = hours.strip()
            address = address.replace(",", " ")
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
            if not city and not state and not pcode:
                temp = (
                    loc.find("div", {"class": "amlocator-info-popup"})
                    .get_text(separator="|", strip=True)
                    .split("|")
                )
                temp = temp[:-3]
                street = (
                    temp[1]
                    .split(
                        ",",
                    )[0]
                    .split("Address: ")[1]
                )
                city = temp[3].split("City: ")[1]
                state = temp[2].split("State: ")[1]
                pcode = temp[4].split("Zip: ")[1]

            data.append(
                [
                    "https://al-ed.com/",
                    link,
                    title.strip(),
                    street.strip(),
                    city.strip(),
                    state.strip(),
                    pcode.strip(),
                    "US",
                    store,
                    phone.strip(),
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()

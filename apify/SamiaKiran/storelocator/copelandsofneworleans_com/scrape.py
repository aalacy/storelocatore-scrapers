import csv
import json
import usaddress
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "copelandsofneworleans_com"
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
    final_data = []
    if True:
        url = "https://copelandsofneworleans.com/locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var address_list_180454c = ")[1].split("}];", 1)[0]
        loclist = loclist + "}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            link = loc["postLink"]
            lat = loc["lat"]
            longt = loc["lng"]
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll("p", {"class": "elementor-icon-box-description"})
            phone = temp[0].text
            hours = temp[1].get_text(separator="|", strip=True).replace("|", " ")
            address = temp[2].get_text(separator="|", strip=True).replace("|", " ")
            log.info(link)
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
            title = city + ", " + state
            final_data.append(
                [
                    "https://copelandsofneworleans.com/",
                    link,
                    title,
                    street.strip(),
                    city.strip(),
                    state.strip(),
                    pcode.strip(),
                    "US",
                    "<MISSING>",
                    phone.strip(),
                    "<MISSING>",
                    lat,
                    longt,
                    hours.strip(),
                ]
            )
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

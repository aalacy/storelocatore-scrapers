from bs4 import BeautifulSoup
import csv
import usaddress
from sgrequests import SgRequests
from sglogging import sglog

website = "excel-urgentcare_com"
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
    data = []
    url = "https://www.excel-urgentcare.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("p")
    if True:
        for loc in loclist:
            if loc.find("a") is None:
                continue
            templist = loc.text.splitlines()
            title = templist[0]
            if "Excel" in title:
                location_type = "Excel Urgent Care"
            else:
                location_type = "Affiliates"
            phone = templist[3]
            try:
                phone = phone.split("Phone:", 1)[1]
            except:
                phone = phone.split("Phone", 1)[1]
            link = loc.find("a")["href"]
            r1 = session.get(link, headers=headers)
            hour = BeautifulSoup(r1.text, "html.parser")
            try:
                hour = hour.find("div", {"class": "fleft schedule"}).text
                if "Schedule: Our Locations are Open" in hour:
                    hours = hour.split("Our Locations are Open", 1)[1].strip()
                elif "Our Locations are Open" in hour:
                    hours = hour.split("Schedule: Our Locations are Open", 1)[1].strip()
                elif "Schedule:" in hour:
                    hours = hour.split("Schedule:", 1)[1].strip()
            except:
                hours = "<MISSING>"
                pass
            address = templist[1] + " " + templist[2]
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
                    street = street.strip()
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                    city = city.strip()
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                    state = state.strip()
                if temp[1].find("ZipCode") != -1:
                    pcode = pcode + " " + temp[0]
                    pcode = pcode.strip()
                i += 1
            if not city:
                city = "<MISSING>"
            data.append(
                [
                    "https://www.excel-urgentcare.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    "<MISSING>",
                    phone,
                    location_type,
                    "<MISSING>",
                    "<MISSING>",
                    hours,
                ]
            )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

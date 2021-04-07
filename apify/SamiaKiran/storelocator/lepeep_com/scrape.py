import csv
import usaddress
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "lepeep_com"
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
        url = "https://lepeep.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "wpsl-stores"}).find("ul").findAll("li")
        for loc in loclist:
            temp = loc.find("div", {"class": "store-address"}).findAll("span")
            temp2 = temp[0].find("a")
            title = temp2.text
            if "Temporarily Closed" in title:
                title = title.replace("Temporarily Closed", " Temporarily Closed")
            if "Open for Indoor Dining" in title:
                title = title.replace(
                    "Open for Indoor Dining", " Open for Indoor Dining"
                )
            if "Now Open" in title:
                title = title.replace("Now Open", " Now Open")
            link = temp2["href"]
            if len(temp) > 4:
                if "(Catering)" not in temp[4].find("a").text:
                    address = temp[2].text + " " + temp[3].text
                    phone = temp[4].find("a").text
                else:
                    address = temp[1].text + " " + temp[2].text
                    phone = temp[3].find("a").text
            else:
                address = temp[1].text + " " + temp[2].text
                phone = temp[3].find("a").text
            try:
                hourlist = (
                    loc.find("div", {"class": "wpsl-store-hours"})
                    .find("table", {"class": "wpsl-opening-hours"})
                    .findAll("tr")
                )
                hours = ""
                for hour in hourlist:
                    hour = hour.findAll("td")
                    day = hour[0].text
                    time = hour[1].text
                    hours = hours + " " + day + " " + time
            except:
                hours = loc.find("div", {"class": "store-column temp-closed-note"}).text
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
            final_data.append(
                [
                    "https://lepeep.com/",
                    link,
                    title.strip(),
                    street.strip(),
                    city.strip(),
                    state.strip(),
                    pcode.strip(),
                    "US",
                    "<MISSING>",
                    phone.strip(),
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
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

import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "unitedok_com"
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
    pattern = re.compile(r"\s\s+")
    if True:
        url = "https://www.unitedok.com/StoreLocator/State/?State=OK"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "table", {"class": "table table-striped table-bordered"}
        ).findAll("tr")
        loclist = loclist[1:]
        for loc in loclist:
            link = loc.findAll("td")[3]
            link = link.find("a")["href"]
            r = session.get(link, headers=headers, verify=False)

            temp = BeautifulSoup(r.text, "html.parser")
            address = temp.find("p", {"class": "Address"}).text.strip()
            address = re.sub(pattern, "\n", str(address)).split("\n")
            phone = temp.find("p", {"class": "PhoneNumber"}).find("a").text
            hours = temp.find("table", {"id": "hours_info-BS"}).find("dd").text
            street = address[1]
            try:
                city = address[2].split(",", 1)[0]
                address = address[2].split(",", 1)[1].split()
                state = address[0]
                pcode = address[1]
            except:
                city = address[2]
                address = address[3].split(",", 1)[1].split()
                state = address[0]
                pcode = address[1]
            title = city
            final_data.append(
                [
                    "https://www.unitedok.com/",
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
        return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

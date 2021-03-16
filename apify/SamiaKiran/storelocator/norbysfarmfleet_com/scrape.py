import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "norbysfarmfleet_com"
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
        url = "http://norbysfarmfleet.com/locations.php"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "location_entry"})
        for loc in loclist:
            store = loc["id"]
            temp = (
                loc.find("td", {"class": "table_info"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            title = temp[0]
            street = temp[1]
            phone = temp[3]
            temp = title.split(",")
            city = temp[0]
            state = temp[1].replace("Warehouse", "")
            link = "http://norbysfarmfleet.com/locations.php#" + store
            hour_list = loc.find("table", {"id": "hours"}).findAll("tr")
            hours = ""
            for hour in hour_list:
                hour = hour.findAll("td")
                day = hour[0].text
                time = hour[1].text
                hours = hours + " " + day + time

            final_data.append(
                [
                    "http://norbysfarmfleet.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    "<MISSING>",
                    "US",
                    store,
                    "<MISSING>",
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

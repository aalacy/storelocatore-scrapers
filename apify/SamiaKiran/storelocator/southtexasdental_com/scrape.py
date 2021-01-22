import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "southtexasdental_com"
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
        url = "https://www.southtexasdental.com/locations"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "view-content"}).findAll(
            "div", {"class": "locations_block"}
        )
        for loc in loclist:
            temp = loc.find("div", {"class": "col-sm-4 address"})
            title = temp.find("h4").find("a").text
            link = temp.find("h4").find("a")["href"]
            link = "https://www.southtexasdental.com" + link
            address = temp.find("p").get_text(separator="|", strip=True).split("|")
            street = address[0]
            address = address[1].split(",", 1)
            city = address[0]
            address = address[1].split()
            state = address[0]
            pcode = address[1]
            phone = (
                loc.find("div", {"class": "col-sm-4 phone"})
                .text.strip()
                .replace("\n", "")
            )
            if "For Braces" in phone:
                phone = phone.split("For Braces", 1)[0]
            hours = (
                loc.find("div", {"class": "col-sm-4 hours"})
                .text.strip()
                .replace("\n", "")
            )
            final_data.append(
                [
                    "https://www.southtexasdental.com/",
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

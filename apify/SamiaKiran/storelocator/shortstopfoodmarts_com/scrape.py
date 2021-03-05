import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "shortstopfoodmarts_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
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
        log.info(f"No of records being processed: {len(temp_list)}")


def fetch_data():
    # Your scraper here
    final_data = []
    if True:
        url = "https://www.shortstopfoodmarts.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "single_stop"})
        for loc in loclist:
            title = loc.find("div", {"class": "location-store"}).find("a").text
            store = title.split()[1]
            address = loc.find("div", {"class": "address"})
            street = address.find("strong").text
            temp = address.text.split(street, 1)[1].split("Phone:", 1)[0].split(",")
            city = temp[0]
            state = temp[1].split("\n")
            pcode = state[1]
            state = state[0]
            phone = address.text.split("Phone:", 1)[1].replace("\n", "")
            hours = (
                loc.find("div", {"class": "details"})
                .find("span", {"class": "letters"})
                .text
            )
            final_data.append(
                [
                    "https://www.shortstopfoodmarts.com/",
                    "https://www.shortstopfoodmarts.com/locations/",
                    title,
                    street,
                    city,
                    state.strip(),
                    pcode,
                    "US",
                    store,
                    phone.strip(),
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

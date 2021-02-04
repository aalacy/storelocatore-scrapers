import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "gelsons_com"
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
        url = "https://www.gelsons.com/stores/store-search-results.html?displayCount=30&state=CA"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = (
            soup.find("div", {"id": "store-search-results"}).find("ul").findAll("li")
        )
        for loc in loclist:
            try:
                title = loc.find("h2", {"class": "store-display-name h6"}).text.strip()
                store = loc["data-storeid"]
                lat = loc["data-storelat"]
                longt = loc["data-storelng"]
                street = loc.find("p", {"class": "store-address"}).text
                temp = loc.find("p", {"class": "store-city-state-zip"}).text
                temp = temp.split(",")
                city = temp[0]
                temp = temp[1].split()
                state = temp[0]
                pcode = temp[1]
                phone = (
                    loc.find("p", {"class": "store-main-phone"})
                    .find("span", {"class": "show-for-medium"})
                    .text
                )
                link = loc.find("a", {"aria-label": title})["href"]
                link = "https://www.gelsons.com" + link
                hours = (
                    loc.find("ul", {"class": "store-regular-hours"})
                    .findAll("li")[1]
                    .text.strip()
                )
            except:
                pass
            final_data.append(
                [
                    "https://www.gelsons.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
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

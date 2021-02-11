import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "emagine-entertainment_com"
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
        url = "https://www.emagine-entertainment.com/theatres/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "theatre-listings"}).findAll(
            "div", {"class": "theatre-listings__theatre"}
        )
        for loc in loclist:
            link = loc.find("a")["href"]
            r = session.get(link, headers=headers, verify=False)
            soup = BeautifulSoup(r.text, "html.parser")
            store = r.text.split("full_address :")[1].split("title :", 1)[0]
            store = store.split('id : "')[1].split('",', 1)[0]
            title = soup.find("h1", {"class": "headline headline--1"}).text
            address = soup.findAll(
                "p", {"class": "theatre-details__sidebar-group-item--address"}
            )
            street = address[0].text
            temp = address[1].text.split(",")
            city = temp[0]
            state = temp[1]
            try:
                phone = (
                    soup.find(
                        "div", {"class": "theatre-details__sidebar-group sbgroup1"}
                    )
                    .find("a")
                    .text.strip()
                )
            except:
                phone = "<MISSING>"
            final_data.append(
                [
                    "https://www.emagine-entertainment.com/",
                    link,
                    title,
                    street,
                    city,
                    state.strip(),
                    "<MISSING>",
                    "US",
                    store,
                    phone,
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
                    "<MISSING>",
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

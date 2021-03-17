import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "primarpetro_com"
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
        url = "https://www.primarpetro.com/locations.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        temp = soup.find("div", {"class": "paragraph"})
        loclist = temp.get_text(separator="|", strip=True).split("|")
        title_list = []
        address_list = []
        for i in range(0, len(loclist)):
            if i % 2:
                address_list.append(loclist[i])
            else:
                title_list.append(loclist[i])
        for (title, address) in zip(title_list, address_list):
            address = address.split(",")
            street = address[0]
            city = address[1]
            address = address[2].split()
            state = address[0]
            pcode = address[1]
            title =  title.replace(":", "")
            store = title.split("#")[1].split("-",1)[0]
            i = i + 2
            final_data.append(
                [
                    "https://www.primarpetro.com/",
                    "https://www.primarpetro.com/locations.html",
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "US",
                    store,
                    "<MISSING>",
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

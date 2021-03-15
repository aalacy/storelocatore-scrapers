import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "fresh_com"
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
        url = "https://www.fresh.com/us/customer-service/USShops.html"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "col-10 col-lg-12 mx-auto text-left"})
        for loc in loclist:
            if len(loc) < 5:
                continue
            else:
                title = loc.find("p", {"class": "subheader1 privacy-info-question"})
                link = title.find("a")["href"]
                title = title.text
                address = (
                    loc.findAll("div")[1].get_text(separator="|", strip=True).split("|")
                )
                street = address[0]
                phone = address[-1]
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                pcode = address[1]
                hours = "<INACCESSIBLE>"
                r = session.get(link, headers=headers, verify=False)
                coords = r.text.split("center=")[1].split("&amp;", 1)[0]
                lat = coords.split("%2C")[0]
                longt = coords.split("%2C")[1]

            final_data.append(
                [
                    "https://www.fresh.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    "USA",
                    "<MISSING>",
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

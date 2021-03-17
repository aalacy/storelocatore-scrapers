import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "eddiemerlots_com"
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
        url = "https://www.eddiemerlots.com/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", href=re.compile("^/locations/"))
        link_list = []
        for loc in loclist:
            link = loc["href"]
            link = "https://www.eddiemerlots.com" + link
            if link not in link_list:
                if link.count("/") > 4:
                    link_list.append(link)
        for link in link_list:
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = (
                soup.find("span", {"id": "fwContent"})
                .find("div")
                .get_text(separator="|", strip=True)
                .split("|")
            )
            title = temp[0]
            phone = temp[-1]
            address = temp[-2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            pcode = address[-1]
            street = temp[-3]
            hour_list = soup.findAll("tbody")[-1].findAll("td")
<<<<<<< Updated upstream
            hours = ""
            for hour in hour_list[0:2]:
                hour = hour.get_text(separator="|", strip=True).replace("|", " ")
                hours = hours + " " + hour
            if not hours:
                hours = "<MISSING>"
=======
            hour_list = soup.find("div", {"id": "rightSideBar"}).findAll("td")
            log.info(link)
            hours = ""
            for hour in hour_list:
                hour = hour.get_text(separator="|", strip=True).replace("|", " ")
                hours = hours + " " + hour
            hours = hours.split("General Manager",1)[0]
>>>>>>> Stashed changes
            final_data.append(
                [
                    "https://www.eddiemerlots.com/",
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

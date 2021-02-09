import csv
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "robeks_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
        for row in data:
            writer.writerow(row)
        log.info(f"No of records being processed: {len(data)}")


def fetch_data():
    # Your scraper here
    data = []
    if True:
        url = "https://robeks.com/ajax/get_gmap_locations.html?is_mobile=&lat=39.11553139999999&lng=-94.62678729999999&radius=3000"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("markers").findAll("marker")
        for loc in loclist:
            if "Coming" in loc["loc_text"]:
                continue
            title = loc["name"]
            link = loc["loc_page_url"]
            link = "https://robeks.com/" + link
            lat = loc["lat"]
            longt = loc["lng"]
            hours = loc["hours"]
            hours = hours.replace("<br />", " ")
            if not hours:
                hours = "<MISSING>"
            templist = loc["contentdesc"].rsplit("<BR />", 1)
            phone = templist[1]
            if not phone:
                phone = "<MISSING>"
            street = loc["address"]
            address = templist[0]
            address = address.replace("<BR />", " ")
            address = address.split(street.upper(), 1)[1].strip()
            address = address.split(",", 1)
            city = address[0]
            temp = address[1].split()
            state = temp[0]
            data.append(
                [
                    "https://robeks.com/",
                    link,
                    title,
                    street,
                    city,
                    state,
                    "<MISSING>",
                    "US",
                    "<MISSING>",
                    phone,
                    "<MISSING>",
                    lat,
                    longt,
                    hours,
                ]
            )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

import csv
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog

website = "rxoptical_com"
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
    data = []
    url = "https://rxoptical.com/wp-admin/admin-ajax.php?action=store_search&lat=42.291707&lng=-85.587229&max_results=25&search_radius=50&autoload=1"
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    for loc in loclist:
        title = loc["store"].replace("&#8217;", " ")
        store = loc["id"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        if not state:
            state = "<MISSING>"
        pcode = loc["zip"]
        ccode = loc["country"]
        if "/" in title:
            link = title.replace(" / ", "-").replace(" ", "-").lower()
            link = "https://rxoptical.com/locations/" + link + "/"
        else:
            link = (
                title.replace(" ", "-").replace("&#8217;", "").replace(".", "").lower()
            )
            link = "https://rxoptical.com/locations/" + link + "/"
        hourlist = loc["hours"]
        if hourlist is None:
            r = session.get(link, headers=headers)
            if "TEMPORARILY CLOSED" in r.text:
                hours = "<MISSING>"
            else:
                continue
        else:
            hourlist = BeautifulSoup(hourlist, "html.parser")
            hourlist = hourlist.findAll("tr")
            hours = ""
            for hour in hourlist:
                temp = hour.findAll("td")
                day = temp[0].text
                time = temp[1].text
                hours = hours + " " + day + " " + time
        data.append(
            [
                "https://rxoptical.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
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


scrape()

import csv
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import sglog

website = "delfriscos_com"
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
    url = "https://delfriscos.com/locations-search/"
    r = session.get(url, headers=headers)
    loclist = r.text.split("ld_locations = ")[1].split("</script><link", 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["city_state"]
        lat = loc["lat"]
        longt = loc["long"]
        phone = loc["phone"]
        temp = loc["address2"]
        if not temp:
            street = loc["address"]
        else:
            street = loc["address"] + "  " + temp
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        link = loc["id"]
        link = "https://delfriscos.com/steakhouse/" + link + "/"
        r = session.get(link, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.find("div", {"id": "col-hours"})
            .find("p")
            .text.split("\n\n", 1)[0]
            .replace("\n", " ")
        )
        data.append(
            [
                "https://delfriscos.com/",
                link,
                title.strip(),
                street.strip(),
                city.strip(),
                state.strip(),
                pcode.strip(),
                "US",
                "<MISSING>",
                phone.strip(),
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

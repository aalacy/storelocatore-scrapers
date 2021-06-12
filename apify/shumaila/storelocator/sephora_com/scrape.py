import csv
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests

from sglogging import sglog

log = sglog.SgLogSetup().get_logger("sephora.com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():
    data = []
    p = 0
    datanow = []
    datanow.append("none")
    url = "https://www.sephora.com/happening/storelist"
    log.info(f"storelist: {url}")
    r = session.get(url, timeout=180, verify=False)
    log.info(f"Res Code: {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=happening]")[6:]
    for link in linklist:
        link = "https://www.sephora.com" + link["href"]
        log.info(f"Scraping data from: {link}")
        r = session.get(link, timeout=180, verify=False)
        log.info(f"Status Code: {r.status_code}")
        try:
            r = r.text.split('"stores":[')[1].split('}],"thirdpartyImageHost"', 1)[0]
        except:
            continue
        r = r + "}"

        loc = json.loads(r)
        street = loc["address"]["address1"]
        try:
            street = street + " " + str(loc["address"]["address2"])
            street = street.replace("None", "").replace("null", "").strip()
        except:
            pass
        ccode = loc["address"]["country"]
        state = loc["address"]["state"]
        city = loc["address"]["city"]
        pcode = loc["address"]["postalCode"]
        phone = loc["address"]["phone"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        store = loc["storeId"]
        ltype = "Store"
        link = "https://www.sephora.com" + loc["targetUrl"]
        title = "Sephora " + loc["displayName"]
        hours = "<MISSING>"
        try:
            hours = (
                "Monday "
                + loc["storeHours"]["mondayHours"]
                + " Tuesday "
                + loc["storeHours"]["tuesdayHours"]
                + " Wednesday "
                + loc["storeHours"]["wednesdayHours"]
                + " Thursday "
                + loc["storeHours"]["thursdayHours"]
                + "Friday "
                + loc["storeHours"]["fridayHours"]
                + " Saturday "
                + loc["storeHours"]["saturdayHours"]
                + " Sunday "
                + loc["storeHours"]["sundayHours"]
            )
            hours = hours.replace("AM", " AM ").replace("PM", " PM ").replace("-", "- ")
        except:
            hours = loc["storeHours"]["closedDays"]
            if hours.find("Opening on") > -1:
                hours = "SOON"
            elif hours.find("closed") > -1:
                hours = "<MISSING>"
        if hours != "SOON":
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(pcode) == 4:
                pcode = "0" + pcode
            if state == "NW":
                state = "WA"
        if store in datanow or "SOON" in hours:
            continue
        datanow.append(store)
        data.append(
            [
                "https://www.sephora.com",
                link,
                title.rstrip().lstrip(),
                street.replace("\r", "").replace("\n", " ").rstrip().lstrip(),
                city.rstrip().lstrip(),
                state.rstrip().lstrip(),
                pcode.rstrip().lstrip(),
                ccode.rstrip().lstrip(),
                store,
                phone.rstrip().lstrip(),
                ltype,
                lat,
                longt,
                hours.rstrip(),
            ]
        )

        p += 1
    log.info(f"Total Locations added: {p}")
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished grabbing locations")


scrape()

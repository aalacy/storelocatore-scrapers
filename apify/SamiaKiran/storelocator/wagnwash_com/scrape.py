import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "wagnwash_com"
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
    url = "https://wagnwash.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find("div", {"class": "row no-gutters p-1 location-boxes"}).findAll(
        "p", {"class": "location-links"}
    )
    for loc in loclist:
        link = loc.find("a")["href"]
        r = session.get(link, headers=headers)
        temp = r.text.split("var locations = [ { ")[1].split(
            ',"fran_add_to_schema"', 1
        )[0]
        temp = "{" + temp + "}"
        temp = json.loads(temp)
        title = temp["name"]
        store = temp["id"]
        lat = temp["latitude"]
        longt = temp["longitude"]
        phone = temp["fran_phone"]
        try:
            street = (
                temp["fran_address"]
                + " "
                + temp["fran_address_2"].replace("&nbsp;", "")
            )
        except:
            street = temp["fran_address"].replace("&nbsp;", "")
        city = temp["fran_city"]
        state = temp["fran_state"]
        pcode = temp["fran_zip"]
        ccode = temp["fran_country"]
        hours = temp["fran_hours"]
        soup = BeautifulSoup(hours, "html.parser")
        hours = soup.find("p").get_text(separator="|", strip=True).split("|")
        if hours[0] == "COVID-19 Adjusted Hours":
            hours = hours[1] + " " + hours[2]
        else:
            hours = hours[0] + " " + hours[1]
        if "Grooming " in hours:
            hours = hours.split("Grooming", 1)[0]
        if "Curbside" in hours:
            hours = hours.split("Curbside", 1)[0]
        data.append(
            [
                "https://wagnwash.com/",
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

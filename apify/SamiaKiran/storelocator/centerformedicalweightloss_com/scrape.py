import csv
import json
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgrequests import SgRequests
from sglogging import sglog

website = "centerformedicalweightloss_com"
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
    data = []
    url = "https://centerformedicalweightloss.com/find_a_center.aspx"
    zips = static_zipcode_list(radius=50, country_code=SearchableCountries.USA)
    for zip_code in zips:
        myobj = {
            "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$ContentBody$Find_A_Center$milesInput": "50",
            "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$ContentBody$Find_A_Center$zipCodeInput": zip_code,
            "ctl00$ctl00$ctl00$ContentPlaceHolderDefault$ContentBody$Find_A_Center$btnSubmit": "SEARCH AGAIN",
            "defaultMiles": "50",
            "__VIEWSTATEGENERATOR": "CA0B0334",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
        }
        r = session.post(url, data=myobj, headers=headers)
        loclist = r.text.split("centersData=")[1].split(";</script></div>", 1)[0]
        loclist = json.loads(loclist)
        for loc in loclist:
            title = loc["name"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            title = loc["name"]
            link = loc["urlslug"]
            link = "https://centerformedicalweightloss.com/doctors?url=" + link
            phone = loc["tollfree"]
            if not phone:
                phone = "<MISSING>"
            street = loc["address1"] + " " + loc["address2"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip"].split("-")[0]
            data.append(
                [
                    "https://centerformedicalweightloss.com/",
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
                    lat,
                    longt,
                    "<MISSING>",
                ]
            )
    return data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


scrape()

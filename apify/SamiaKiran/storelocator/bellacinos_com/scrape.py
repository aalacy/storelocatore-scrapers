import csv
import json
from datetime import datetime
from sgrequests import SgRequests
from sglogging import sglog

website = "bellacinos_com"
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
    url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=BAVYISWKYNNQTIXK&center=31.8039734986,-98.8223185136653&coordinates=10.74167474861858,-141.02202554491512,37.493303137349145,-106.62261148241522&multi_account=false&page=1&pageSize=60"
    r = session.get(url, headers=headers)
    loclist = r.text
    loclist = json.loads(loclist)
    for loc in loclist:

        phone = loc["store_info"]["phone"]
        title = loc["store_info"]["name"]
        street = loc["store_info"]["address"]
        city = loc["store_info"]["locality"]
        state = loc["store_info"]["region"]
        pcode = loc["store_info"]["postcode"]
        ccode = loc["store_info"]["country"]
        store = loc["store_info"]["corporate_id"]
        lat = loc["store_info"]["latitude"]
        longt = loc["store_info"]["longitude"]
        temp = loc["store_info"]["store_hours"]
        temp = temp.split(";", 1)[0]
        temp = temp.split(",")
        open_time = temp[1]
        open_time = open_time[0:2] + ":" + open_time[2:4]
        open_time = datetime.strptime(open_time, "%H:%M")
        open_time = open_time.strftime("%I:%M %p")
        close = temp[2]
        close = close[0:2] + ":" + close[2:4]
        close = datetime.strptime(close, "%H:%M")
        close = close.strftime("%I:%M %p")
        hours = open_time + " - " + close
        final_data.append(
            [
                "https://bellacinos.com/",
                "https://locations.bellacinos.com/",
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
    return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

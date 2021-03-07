import csv
import json
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

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
    daylist = {
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursday",
        "5": "Friday",
        "6": "Saturday",
        "7": "Sunday",
    }
    url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=BAVYISWKYNNQTIXK&center=31.8039734986,-98.8223185136653&coordinates=10.74167474861858,-141.02202554491512,37.493303137349145,-106.62261148241522&multi_account=false&page=1&pageSize=60"
    r = session.get(url, headers=headers)
    loclist = json.loads(r.text)
    link_list = "https://locations.bellacinos.com/sitemap.xml"
    r = session.get(link_list, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    link_list = soup.findAll("loc")
    for loc in loclist:
        phone = loc["store_info"]["phone"]
        title = loc["store_info"]["name"]
        temp = loc["store_info"]["address"]
        temp = temp.replace(" ", "-")
        for link in link_list:
            link = str(link)
            if temp in link:
                link = (
                    link.replace("<loc>", "")
                    .replace("</loc>", "")
                    .replace(
                        "https://locations.bellacinosgrinders.com/",
                        "https://locations.bellacinos.com/",
                    )
                )
                break
        try:
            street = (
                loc["store_info"]["address"]
                + " "
                + loc["store_info"]["address_extended"]
            )
        except:
            street = loc["store_info"]["address"]
        city = loc["store_info"]["locality"]
        state = loc["store_info"]["region"]
        pcode = loc["store_info"]["postcode"]
        ccode = loc["store_info"]["country"]
        store = loc["store_info"]["corporate_id"]
        lat = loc["store_info"]["latitude"]
        longt = loc["store_info"]["longitude"]
        hour_list = loc["store_info"]["store_hours"]
        hour_list = hour_list.split(";")
        hours = ""
        for hour in hour_list[:-1]:
            hour = hour.split(",")
            day = daylist[hour[0]]
            open_time = hour[1]
            close_time = hour[2]
            hours = hours + day + " " + open_time + " - " + close_time + " "
        final_data.append(
            [
                "https://bellacinos.com/",
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
    return final_data


def scrape():
    log.info("Started")
    data = fetch_data()
    write_output(data)
    log.info("Finished")


if __name__ == "__main__":
    scrape()

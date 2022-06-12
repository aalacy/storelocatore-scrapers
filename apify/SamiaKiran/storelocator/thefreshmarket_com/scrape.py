import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "thefreshmarket_com"
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
    url = "https://www.thefreshmarket.com/your-market/store-locator"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"relocating"')[1:]  # .split(',"data":{},"seo"', 1)[0]
    flag = 0
    for loc in loclist:
        loc = loc.split(",", 1)[1].split("},{", 1)[0]
        loc = "{" + loc + "}"
        try:
            loc = json.loads(loc)
        except:
            loc = loc.split('],"allUsaStates"')[0]
            loc = json.loads(loc.replace("]}", ""))
            flag = 1
        if flag == 1:
            break
        title = loc["storeName"]
        store = loc["storeNumber"]
        lat = loc["storeLocation"]["lat"]
        longt = loc["storeLocation"]["lon"]
        phone = loc["phoneNumber"]
        street = loc["address"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["postalCode"]
        hours = loc["moreStoreHours"]
        link = loc["slug"]
        link = "https://www.thefreshmarket.com/my-market/store/" + link
        data.append(
            [
                "https://www.thefreshmarket.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
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

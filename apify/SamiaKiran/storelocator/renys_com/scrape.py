import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "renys_com"
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
    url = "https://www.renys.com/pages/hours-locations"
    r = session.get(url, headers=headers)
    loclist = r.text.split("stores = [")[1].split("</script>", 1)[0]
    loclist = "[" + loclist.rsplit("},", 1)[0] + "}]"
    loclist = json.loads(loclist)
    for loc in loclist:
        title = loc["store_name"]
        address = loc["address"]
        address = address.split("<br>")
        street = " ".join(address[0:-1])
        address = address[-1].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        pcode = address[1]
        phone = loc["phone"]
        hours = loc["hours_line_1"] + " " + loc["hours_line_2"]
        data.append(
            [
                "https://www.renys.com/",
                "https://www.renys.com/pages/hours-locations",
                title.strip(),
                street,
                city.strip(),
                state.strip(),
                pcode.strip(),
                "US",
                "<MISSING>",
                phone.strip(),
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
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

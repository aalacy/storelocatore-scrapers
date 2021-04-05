import csv
import json
from sgrequests import SgRequests
from sglogging import sglog

website = "maxmuscle_com"
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
    url = "https://stores.maxmuscle.com/"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"dataLocations":')[1].split(',"uiLocationsList"', 1)[0]
    loclist = loclist + "}"
    loclist = json.loads(loclist)["collection"]["features"]
    for loc in loclist:
        store = str(loc["properties"]["id"])
        url = (
            "https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/dGjlgtMJqgG6qChVmvGiUwLD49pK8Z/locations-details?locale=en_US&ids="
            + store
            + "&clientId=590b4375866d3a33468eef69&cname=stores.maxmuscle.com"
        )
        r = session.get(url, headers=headers)
        temp = r.text.split('"features":[')[1].split(',"cmsFeatures":', 1)[0]
        temp = temp + "}}"
        temp = json.loads(temp)
        coord = (
            str(temp["geometry"]["coordinates"])
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        longt = coord[0]
        lat = coord[1]
        store = temp["properties"]["branch"]
        title = temp["properties"]["name"]
        street1 = temp["properties"]["addressLine1"]
        street2 = temp["properties"]["addressLine2"]
        if not street2:
            street = street1
        else:
            street = street1 + " " + street2
        city = temp["properties"]["city"]
        state = temp["properties"]["province"]
        pcode = temp["properties"]["postalCode"]
        ccode = temp["properties"]["country"]
        phone = temp["properties"]["phoneLabel"]
        link = temp["properties"]["slug"]
        link = "https://stores.maxmuscle.com/" + link

        hours = (
            str(temp["properties"]["hoursOfOperation"])
            .replace("{", "")
            .replace("}", "")
            .replace("[[", "")
            .replace("]]", "")
            .replace("'", "")
            .replace(",", " ")
        )
        if "[]" in hours:
            hours = hours.replace("[]", " Closed")
        data.append(
            [
                "https://maxmuscle.com/",
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

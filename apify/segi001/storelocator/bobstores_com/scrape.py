import csv
import sgrequests
import json


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
    # Your scraper here
    locator_domain = "https://www.bobstores.com/"

    missingString = "<MISSING>"

    def retrieveStores():
        api = "https://www.bobstores.com/api/stores"
        return json.loads(sgrequests.SgRequests().get(api).text)

    stores = retrieveStores()

    result = []

    for s in stores:
        name = s["title"]
        city = s["addressLocality"]
        zp = s["addressPostalCode"]
        state = s["addressRegion"]
        code = s["country"]
        street = s["addressStreet"]
        lat = s["coordinates"]["lat"]
        lng = s["coordinates"]["lng"]
        phone = s["telephone"]
        url = "{}{}".format("https://www.bobstores.com/stores/", s["slug"])
        storenum = s["id"]
        timeArray = []
        for t in s["hoursOfOperation"]:
            timeArray.append("{} : {} - {}".format(t["day"], t["open"], t["closed"]))
        hours = ", ".join(timeArray)
        ty = missingString
        if not hours:
            ty = "Closed"
            hours = missingString
        result.append(
            [
                locator_domain,
                url,
                name,
                street,
                city,
                state,
                zp,
                code,
                storenum,
                phone,
                ty,
                lat,
                lng,
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

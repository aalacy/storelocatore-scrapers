import csv
import sgrequests
import json


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8") as output_file:
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
    locator_domain = "https://www.drmartens.com/uk/en_gb/"
    api = "https://www.drmartens.com/uk/en_gb/store-finder?q=London&page="
    missingString = "<MISSING>"

    pages = 4

    data = []

    for p in range(pages):
        sess = sgrequests.SgRequests()
        req = json.loads(sess.get("{}{}".format(api, p)).text)
        for d in req["data"]:
            data.append(d)

    result = []

    for s in data:
        name = s["name"]
        url = "{}{}".format("https://www.drmartens.com/uk/en_gb", s["url"])
        phone = s["phone"].replace("Phone: ", "").replace('"Tel.: ', "")
        city = s["town"]
        zp = s["postalCode"]
        if not zp:
            zp = missingString
        if not phone:
            phone = missingString
        lat = s["latitude"]
        lng = s["longitude"]
        street = "{} {}".format(s["line1"], s["line2"])
        timeArray = []
        for hour in s["openings"]:
            timeArray.append("{} : {}".format(hour, s["openings"][hour]))
        hours = ", ".join(timeArray)
        result.append(
            [
                locator_domain,
                url,
                name,
                street,
                city,
                missingString,
                zp,
                missingString,
                missingString,
                phone,
                missingString,
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

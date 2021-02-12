import csv
import sgrequests
import json
import itertools


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
    missingString = "<MISSING>"

    data = []

    def endpoint(city, pages, data):
        api = "https://www.drmartens.com/intl/en/store-finder?q={}&page=".format(city)
        for p in range(pages):
            sess = sgrequests.SgRequests()
            req = json.loads(sess.get("{}{}".format(api, p)).text)
            for d in req["data"]:
                data.append(json.dumps(d))

    endpoint("London", 4, data)
    endpoint("Paris", 2, data)
    endpoint("Dublin", 1, data)
    endpoint("UK", 1, data)
    endpoint("France", 2, data)
    endpoint("all", 24, data)

    result = []

    def hasHours(stri):
        return any(char.isdigit() for char in stri)

    for ss in set(data):
        s = json.loads(ss)
        name = s["name"]
        url = "{}{}".format("https://www.drmartens.com/intl/en/", s["url"])
        phone = (
            s["phone"]
            .replace("Phone: ", "")
            .replace('"Tel.: ', "")
            .replace("Tél. : +", "")
        )
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
        hours = missingString
        typ = missingString
        if "openings" in s:
            for hour in s["openings"]:
                timeArray.append("{} : {}".format(hour, s["openings"][hour]))
            hours = ", ".join(timeArray)
        if not hasHours(hours):
            hours = missingString
            typ = "Temporary Closed"
        if city == "":
            city = missingString
        if float(lat) == 0:
            lat = missingString
        if float(lng) == 0:
            lng = missingString
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
                typ,
                lat,
                lng,
                hours,
            ]
        )
    result = list(result for result, _ in itertools.groupby(result))
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

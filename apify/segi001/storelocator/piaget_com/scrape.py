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
    locator_domain = "https://www.piaget.com/"
    missingString = "<MISSING>"

    def r(l):
        return sgrequests.SgRequests().get(l)

    def fetch():
        a = r("https://www.piaget.com/gb-en/api/search/store/locator")
        j = json.loads(a.text)
        return j

    s = fetch()

    result = []

    def scrape(e, result):
        timeSelector = e["openingHours"]
        timeArray = []
        for days in timeSelector:
            if timeSelector[days]["isClosed"] == "false":
                timeArray.append(
                    days
                    + " : "
                    + timeSelector[days]["openIntervals"][0]["start"]
                    + " - "
                    + timeSelector[days]["openIntervals"][0]["end"]
                )
            else:
                pass
        hours = ", ".join(timeArray)
        if hours == "":
            hours = missingString
        result.append(
            [
                locator_domain,
                e["permalink"],
                e["name"],
                e["address1"] + " " + e["address2"],
                e["city"],
                e["country"],
                e["zip"],
                missingString,
                e["id"],
                e["phone"],
                e["type"],
                e["lat"],
                e["lng"],
                hours,
            ]
        )

    for e in s["data"]:
        if "United Kingdom" in e["country"]:
            if "boutique" in e["type"]:
                scrape(e, result)
        if "United States of America" in e["country"]:
            if "boutique" in e["type"]:
                scrape(e, result)
        if "Canada" in e["country"]:
            if "boutique" in e["type"]:
                scrape(e, result)
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

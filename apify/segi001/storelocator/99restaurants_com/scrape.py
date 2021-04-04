import csv
from sgrequests import SgRequests
import bs4


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
    locator_domain = "https://www.99restaurants.com/"
    allLocationsURL = "https://www.99restaurants.com/all-locations/"
    missingString = "<MISSING>"

    s = SgRequests()

    allLocationHTML = s.get(allLocationsURL).text

    soup = bs4.BeautifulSoup(allLocationHTML, features="lxml")

    allLocationsArray = soup.findAll("a", {"class": "locationslist__name"})

    result = []

    def ruleset(string):
        lst = (
            string.replace("Indoor Seating", "")
            .replace(
                "Save time with Call Ahead Seating.Curbside Pickup and Delivery Service Available.",
                "",
            )
            .strip()
            .replace("PM", "PM\n")
            .split("\n")
        )
        if len(lst) > 2:
            return "{}, {}, {}".format(lst[0], lst[2], lst[3])
        return missingString

    for location in allLocationsArray:
        location_url = locator_domain + location["href"]
        s2 = SgRequests()
        locationHTML = s2.get(location_url).text
        soup2 = bs4.BeautifulSoup(locationHTML, features="lxml")
        name = soup2.findAll("h1", {"class": "locinfo__headline headline"})[0].text
        addressinfo = soup2.findAll(
            "h2", {"class": "locinfo__subheadline subheadline"}
        )[0].text
        phone = soup2.findAll("a", {"class": "locinfo__location-phone"})[0].text.strip()
        hours = soup2.findAll("div", {"class": "locinfo__location-hours-content"})[
            0
        ].text

        addressJSON = {}
        infoArray = []

        for el in addressinfo.split("\n"):
            infoArray.append(el.strip().replace(",", ""))

        addressJSON = {
            "street": infoArray[1],
            "city": infoArray[2],
            "country": infoArray[3],
            "zip": infoArray[4],
        }
        result.append(
            [
                locator_domain,
                location_url,
                name,
                addressJSON["street"],
                addressJSON["city"],
                addressJSON["country"],
                addressJSON["zip"],
                missingString,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                ruleset(hours),
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

import csv
import sgrequests
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
    locator_domain = "https://www.haleandhearty.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initS(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    s = initS("https://www.haleandhearty.com/locations/")

    result = []

    for l in s.findAll("div", {"class": "location-card"}):
        name = l.find("h3", {"class": "location-card__name"}).text.strip()
        phone = l.find("p", {"class": "location-card__phone"}).text.strip()
        street = l.find("p").text.strip()
        hours = (
            l.find("p", {"class": "location-card__hours-today"})
            .text.replace("Store Hours:", "")
            .strip()
        )
        result.append(
            [
                locator_domain,
                missingString,
                name,
                street,
                missingString,
                missingString,
                missingString,
                missingString,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

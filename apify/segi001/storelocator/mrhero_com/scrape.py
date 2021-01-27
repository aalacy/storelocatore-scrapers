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
    locator_domain = "https://www.mrhero.com/"
    stores_xml = "https://www.mrhero.com/webapp-locations-action?xml=yes&lat=&lng=&radius=1000000"
    missingString = "<MISSING>"
    storeNames = "Mr. Hero"

    s = SgRequests()
    xml = s.get(stores_xml).text
    soup = bs4.BeautifulSoup(xml, features="lxml")

    marker = soup.findAll("marker")

    result = []

    for el in marker:
        result.append(
            [
                locator_domain,
                missingString,
                storeNames,
                el["address"],
                el["city"],
                el["state"],
                el["zip"],
                missingString,
                el["id"],
                el["phone"],
                missingString,
                el["lat"],
                el["lng"],
                "Monday : {} ; Tuesday : {} ; Wednesday : {} ; Thursday : {} ; Friday : {} ; Saturday : {} ; Sunday : {} ; ".format(
                    el["monday"],
                    el["tuesday"],
                    el["wednesday"],
                    el["thursday"],
                    el["friday"],
                    el["saturday"],
                    el["sunday"],
                ),
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

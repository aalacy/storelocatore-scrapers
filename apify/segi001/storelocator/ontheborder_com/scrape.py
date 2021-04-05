import csv
from sgrequests import SgRequests
import json
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

    s = SgRequests()
    html = s.get("https://www.ontheborder.com/sitemap.xml").content
    soup = bs4.BeautifulSoup(html, features="lxml")
    loc = soup.findAll("loc")

    locatorDomain = "https://www.ontheborder.com/"
    slugURL = "https://www.ontheborder.com/location/"
    apiURL = "https://www.ontheborder.com/Locations/GetLocationBySlug/"

    result = []

    for locs in loc:
        if slugURL in locs.text:
            s1 = SgRequests()
            slug = locs.text.replace(slugURL, "")
            jsonData = json.loads(s1.get(apiURL + slug).content)
            result.append(
                [
                    locatorDomain,
                    locs.text,
                    jsonData["Name"],
                    jsonData["Address"],
                    jsonData["City"],
                    jsonData["State"],
                    jsonData["Zip"],
                    jsonData["State"],
                    jsonData["StoreNumber"],
                    jsonData["Phone"],
                    "<MISSING>",
                    jsonData["Latitude"],
                    jsonData["Longitude"],
                    jsonData["RestaurantHours"],
                ]
            )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

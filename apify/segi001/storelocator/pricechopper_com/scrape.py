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

    locatorURL = "https://stores.pricechopper.com"
    sitemapURL = "https://stores.pricechopper.com/sitemap.xml"
    storeURL = "https://stores.pricechopper.com/ll/US/"
    apiURL = "https://api.momentfeed.com/v1/analytics/api/llp.json"
    apiAUTH = "XUWEWBYNKILCHSRT"
    missingString = "<MISSING>"

    sitemapHTML = s.get(sitemapURL).text

    soup = bs4.BeautifulSoup(sitemapHTML, features="lxml")

    locations = soup.findAll("loc")

    result = []

    country_code = ""

    def ruleset(string):
        return (
            string.replace("-", " ")
            .replace("_", ".")
            .replace("+~", "&")
            .replace("*", ",")
            .replace("~", "-")
        )

    for loc in locations:
        dataArray = loc.text.replace(storeURL, "").split("/")

        address = ruleset(dataArray[2])
        locality = ruleset(dataArray[1])
        region = dataArray[0]

        data = {
            "auth_token": apiAUTH,
            "address": address,
            "locality": locality,
            "region": region,
        }

        s2 = SgRequests()

        jsonData = json.loads(s2.get(apiURL, params=data).text)

        if jsonData[0]["store_info"]["country"] == "US":
            country_code = "+1"

        result.append(
            [
                locatorURL,
                loc.text,
                jsonData[0]["store_info"]["name"],
                jsonData[0]["store_info"]["address"],
                jsonData[0]["store_info"]["locality"],
                jsonData[0]["store_info"]["region"],
                jsonData[0]["store_info"]["postcode"],
                country_code,
                jsonData[0]["store_info"]["corporate_id"],
                jsonData[0]["store_info"]["phone"],
                missingString,
                jsonData[0]["store_info"]["latitude"],
                jsonData[0]["store_info"]["longitude"],
                jsonData[0]["store_info"]["store_hours"],
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

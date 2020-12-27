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

    locator_domain = "https://www.slumberland.com/"
    storeSitemap = "https://www.slumberland.com/sitemap_stores.xml"

    missingString = "<MISSING>"

    html = s.get(storeSitemap).text
    soup = bs4.BeautifulSoup(html, features="lxml")

    loc = soup.findAll("loc")

    result = []

    for locs in loc:
        s1 = SgRequests()
        html1 = s1.get(locs.text).text
        soup1 = bs4.BeautifulSoup(html1, features="lxml")
        jsonld = soup1.find("script", {"type": "application/ld+json"})
        if jsonld:
            jsonData = json.loads(jsonld.contents[0].replace("\r", ""), strict=False)
            if jsonData["name"] == "null":
                pass
            else:
                result.append(
                    [
                        locator_domain,
                        jsonData["url"],
                        jsonData["name"],
                        jsonData["address"]["streetAddress"],
                        jsonData["address"]["addressLocality"],
                        jsonData["address"]["addressRegion"],
                        jsonData["address"]["postalCode"],
                        missingString,
                        missingString,
                        jsonData["telephone"],
                        jsonData["@type"],
                        jsonData["location"]["geo"]["latitude"],
                        jsonData["location"]["geo"]["longitude"],
                        jsonData["openingHours"][0],
                    ]
                )
        else:
            pass

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

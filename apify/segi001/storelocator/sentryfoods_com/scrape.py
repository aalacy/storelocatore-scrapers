import csv
import sgrequests
import bs4
import re


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
    locator_domain = "https://www.sentryfoods.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initSoup(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    def returnAllStores():
        s = initSoup(
            "https://www.sentryfoods.com/content/svu-retail-independents/s/sentryfoods/en/stores-sitemap.xml"
        )
        res = []
        for loc in s.findAll("loc"):
            res.append(loc.text.strip())
        return res

    stores = returnAllStores()
    result = []

    for store in stores:
        s = initSoup(store)
        name = s.find("h2", {"itemprop": "name"}).text.strip()
        if name == "":
            pass
        else:
            street = s.find("span", {"itemprop": "streetAddress"}).text
            city = s.find("span", {"itemprop": "addressLocality"}).text
            state = s.find("span", {"itemprop": "addressRegion"}).text
            zp = s.find("span", {"itemprop": "postalCode"}).text
            phone = s.find("a", {"itemprop": "telephone"}).text
            hours = s.find("span", {"itemprop": "openingHours"}).text
            url = store
            lat = re.search(r'storeLat = "(.*?)";', str(s)).group(1)
            lng = (
                re.search(r'storeLng = "(.*?)";', str(s))
                .group(1)
                .replace(r"\u002D", "")
            )
            result.append(
                [
                    locator_domain,
                    url,
                    name,
                    street,
                    city,
                    state,
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

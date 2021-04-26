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
    locator_domain = "https://www.pioneer.ca/"
    missingString = "<MISSING>"

    def r(l):
        return sgrequests.SgRequests().get(l)

    def s(l):
        req = r(l)
        return [req.text, bs4.BeautifulSoup(req.text, features="lxml")]

    def allStores():
        so = s("https://www.pioneer.ca/sitemap-stores.xml")[1]
        res = []
        for e in so.findAll("loc"):
            res.append(e.text)
        return res

    storeLinks = allStores()

    def areValidHours(h):
        return any(char.isdigit() for char in h)

    result = []

    for link in storeLinks:
        so = s(link)
        addrGroup = so[1].findAll("span", {"class": "station__coordinates-line"})
        name = so[1].find("h2", {"class": "station__title"}).text
        url = link
        street = addrGroup[0].text
        city = addrGroup[1].text.strip().split(",")[0].strip()
        state = addrGroup[1].text.strip().split(",")[1].strip().split(" ")[0]
        zp = (
            addrGroup[1]
            .text.strip()
            .replace(city, "")
            .replace(state, "")
            .strip()
            .replace(",", "")
            .strip()
        )
        phone = so[1].find("a", {"class": "station__coordinates-line"}).text.strip()
        lat = re.search(r"lat: (.*?),", so[0]).group(1)
        lng = re.search(r"lng: (.*)", so[0]).group(1)
        h = so[1].find("h4", {"class": "icons-list-icon-title"}).text
        if not areValidHours(h):
            h = missingString
        if phone == "":
            phone = missingString
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
                h,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

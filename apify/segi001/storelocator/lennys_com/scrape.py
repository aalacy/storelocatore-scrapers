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
    locator_domain = "https://www.lennys.com/"
    url = "https://www.lennys.com/locations/"
    missingString = "<MISSING>"

    sess = sgrequests.SgRequests()

    s = bs4.BeautifulSoup(sess.get(url).text, features="lxml").findAll(
        "area", href=True
    )

    urls = []

    for slug in s:
        url1 = "{}{}".format(locator_domain, slug["href"].replace("/", "", 1))
        urls.append(url1)

    urlSlugs = []

    for us in urls:
        s1 = bs4.BeautifulSoup(sess.get(us).text, features="lxml")
        slugs = s1.findAll("a", href=True)
        for a in slugs:
            sl = a["href"]
            if "locations" in sl:
                if sl == "/locations/":
                    pass
                else:
                    urlSlugs.append(sl)

    setToList = list(set(urlSlugs))

    result = []

    def getLatLng(html):
        latlng = (
            re.search(r"center: {(.*?)},", str(html))
            .group(1)
            .replace("lat:", "")
            .replace(", lng:", "")
            .strip()
        )
        return latlng.split(" ")

    for uri in setToList:
        finalStoreURL = "{}{}".format(locator_domain, uri.replace("/", "", 1))
        soup = bs4.BeautifulSoup(sess.get(finalStoreURL).text, features="lxml")
        name = soup.find("h2")
        if not name:
            pass
        else:
            result.append(
                [
                    locator_domain,
                    finalStoreURL,
                    name.text,
                    soup.find("span", {"itemprop": "streetAddress"}).text,
                    soup.find("span", {"itemprop": "addressLocality"}).text,
                    soup.find("span", {"itemprop": "addressRegion"}).text,
                    soup.find("span", {"itemprop": "postalCode"}).text,
                    missingString,
                    "".join(filter(str.isdigit, name.text)),
                    soup.find("span", {"itemprop": "telephone"}).text,
                    missingString,
                    getLatLng(soup)[0],
                    getLatLng(soup)[1],
                    missingString,
                ]
            )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

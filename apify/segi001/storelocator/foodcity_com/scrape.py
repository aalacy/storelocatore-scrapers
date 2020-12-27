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
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }

    locator_domain = "https://www.foodcity.com/"

    def returnAllStores(limiter):
        storeLocator = "https://www.foodcity.com/index.php?vica=ctl_storelocations&vicb=showNextStoresForStoreSelector&vicc=p&Lat=42.3576&Lng=-71.0514&Radius=&Address=&pageCount="
        i = 0
        res = []
        while i < limiter:
            i += 10
            s = SgRequests()
            u = "{}{}".format(storeLocator, i)
            html = s.get(u, headers=headers).text
            soup = bs4.BeautifulSoup(html, features="lxml")
            urls = soup.findAll("div", {"class": "store-name"})
            for url in urls:
                res.append("{}{}".format(locator_domain, url.find("p")["href"]))
        return res

    stores = returnAllStores(140)

    missingString = "<MISSING>"

    result = []

    for store in stores:
        s = SgRequests()
        html = s.get(store, headers=headers).text
        soup = bs4.BeautifulSoup(html, features="lxml")
        name = soup.find("a", {"href": store.replace(locator_domain, "")}).text.strip()
        storeID = name.split(" ")[2].replace("#", "").strip()
        address = soup.find("input", {"id": "Address{}".format(storeID)})["value"]
        city = soup.findAll("span", {"class": "city"})[0].text.strip()
        state = soup.find("input", {"id": "State{}".format(storeID)})["value"]
        postal = soup.findAll("span", {"class": "postal-code"})[0].text.strip()
        phone = soup.findAll("div", {"class": "tel"})[0].text.strip()
        lat = soup.find("input", {"id": "lat{}".format(storeID)})["value"]
        lng = soup.find("input", {"id": "lng{}".format(storeID)})["value"]
        storeHours = soup.find("input", {"id": "StoreHours{}".format(storeID)})["value"]

        result.append(
            [
                locator_domain,
                store,
                name,
                address,
                city,
                state,
                postal,
                missingString,
                storeID,
                phone,
                missingString,
                lat,
                lng,
                storeHours.replace("(", "")
                .replace(")", ":")
                .replace("M", "Monday")
                .replace("F", "Friday"),
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

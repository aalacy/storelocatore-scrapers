import csv
import sgrequests
import re
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
    locator_domain = "https://www.abuelos.com/"
    missingString = "<MISSING>"

    def fetchAllStores():
        site = sgrequests.SgRequests().get("https://www.abuelos.com/restaurants/").text
        js = (
            re.search(r"(?sm)window.locations = \[(.*?)\];", site).group(1).strip()[:-1]
        )
        loc_url = re.findall(r"permalink: '(.*?)'", js)
        ln = re.findall(r"latlng: (.*?)},", js)
        latlng = []
        for el in ln:
            latlng.append(
                el.replace("{", "")
                .replace("lat:", "")
                .replace("lng:", "")
                .replace(" ", "")
                .strip()
                .split(",")
            )
        tup = list(zip(loc_url, latlng))
        res = []
        for el in tup:
            s = sgrequests.SgRequests().get(el[0]).text
            a = re.findall(
                r'(?sm)<script type="application/ld\+json">(.*?)</script>', s
            )[1]
            openingHours = re.search(r'(?sm)"openingHours": (.*?)],', a).group(1)
            a = a.replace('"openingHours":', "").replace(openingHours + "],", "")
            ld = json.loads(a)
            soup = bs4.BeautifulSoup(s, features="lxml")
            times = soup.findAll("td", {"class": "hours_day"})
            timeArray = []
            for day in times:
                timeArray.append("{} : {}".format(day.text, day.find_next("td").text))
            hours = ", ".join(timeArray)
            if not hours:
                hours = missingString
            res.append(
                {
                    "locator_domain": locator_domain,
                    "page_url": el[0],
                    "name": ld["name"],
                    "street": ld["address"]["streetAddress"],
                    "city": ld["address"]["addressLocality"],
                    "state": ld["address"]["addressRegion"],
                    "zip": ld["address"]["postalCode"],
                    "code": ld["address"]["addressCountry"],
                    "store_num": missingString,
                    "phone": ld["telephone"],
                    "type": missingString,
                    "lat": el[1][0],
                    "lng": el[1][1],
                    "hours": hours,
                }
            )
        return res

    stores = fetchAllStores()

    result = []

    for s in stores:
        result.append(
            [
                s["locator_domain"],
                s["page_url"],
                s["name"],
                s["street"],
                s["city"],
                s["state"],
                s["zip"],
                s["code"],
                s["store_num"],
                s["phone"],
                s["type"],
                s["lat"],
                s["lng"],
                s["hours"],
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

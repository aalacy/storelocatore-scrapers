import csv
from sgrequests import SgRequests
import bs4
import json


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
    locator_domain = "https://www.pepboys.com/tires"
    storeUrl = "https://stores.pepboys.com/"
    allStoresUrl = "https://stores.pepboys.com/index.html"

    def allStores():
        res = []
        s = SgRequests()
        html = s.get(allStoresUrl).text
        soup = bs4.BeautifulSoup(html, features="lxml")
        stateLinks = soup.findAll("a", {"class": "c-directory-list-content-item-link"})
        cityLinks = []
        for link in stateLinks:
            s1 = SgRequests()
            html1 = s1.get("{}{}".format(storeUrl, link["href"])).text
            soup1 = bs4.BeautifulSoup(html1, features="lxml")
            cityL = soup1.findAll("a", {"class": "c-directory-list-content-item-link"})
            cityLinks.append(cityL)
        for el in cityLinks:
            for citylink in el:
                s2 = SgRequests()
                html2 = s2.get("{}{}".format(storeUrl, citylink["href"])).text
                soup2 = bs4.BeautifulSoup(html2, features="lxml")
                moreS = soup2.findAll("a", {"data-ya-track": "other_details"})
                if not moreS:
                    res.append("{}{}".format(storeUrl, citylink["href"]))
                else:
                    for st in moreS:
                        res.append(
                            "{}{}".format(storeUrl, st["href"].replace("../", ""))
                        )
        return res

    def parseHour(string, char):
        reverse = str(string)[::-1]
        count = 0
        new = ""
        for num in reverse:
            count += 1
            new += num
            if count == 2:
                new += char
        return new[::-1]

    stores = allStores()

    s = SgRequests()

    missingString = "<MISSING>"

    result = []

    for store in stores:
        html = s.get(store).text
        soup = bs4.BeautifulSoup(html, features="lxml")
        name = soup.find("h1", {"id": "location-name"}).text.strip()
        address = soup.findAll("span", {"class": "c-address-street-1"})[0].text.strip()
        city = soup.find("span", {"itemprop": "addressLocality"}).text.strip()
        state = missingString
        if not soup.find("abbr", {"itemprop": "addressRegion"}):
            pass
        else:
            state = soup.find("abbr", {"itemprop": "addressRegion"}).text.strip()
        zipC = soup.find("span", {"itemprop": "postalCode"}).text.strip()
        phone = soup.find("a", {"data-ya-track": "phonecall"}).text.strip()
        hours = json.loads(
            soup.find(
                "div", {"class": "c-location-hours-details-wrapper js-location-hours"}
            )["data-days"]
        )
        t = []
        for time in hours:
            if not time["intervals"]:
                t.append("{} : Closed".format(time["day"]))
            else:
                day = ""
                if time["day"] == "MONDAY":
                    day = "Mon"
                elif time["day"] == "TUESDAY":
                    day = "Tue"
                elif time["day"] == "WEDNESDAY":
                    day = "Wed"
                elif time["day"] == "THURSDAY":
                    day = "Thu"
                elif time["day"] == "FRIDAY":
                    day = "Fri"
                elif time["day"] == "SATURDAY":
                    day = "Sat"
                elif time["day"] == "SUNDAY":
                    day = "Sun"
                t.append(
                    "{} : {}AM - {}PM".format(
                        day,
                        parseHour(time["intervals"][0]["start"], ":"),
                        parseHour(time["intervals"][0]["end"], ":"),
                    )
                )
        hours_of_operation = ", ".join(t)
        result.append(
            [
                locator_domain,
                store,
                name,
                address,
                city,
                state,
                zipC,
                missingString,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hours_of_operation,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

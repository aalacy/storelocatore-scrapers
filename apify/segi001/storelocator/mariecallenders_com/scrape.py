import csv
import sgrequests
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
    locator_domain = "https://www.mariecallenders.com/"
    missingString = "<MISSING>"

    def retrieveStates():
        s = bs4.BeautifulSoup(
            sgrequests.SgRequests()
            .get("https://www.mariecallenders.com/locations")
            .text,
            features="lxml",
        )
        res = []
        ul = s.find("ul", {"class": "state-menu"})
        ass = ul.findAll("a", href=True)
        for a in ass:
            res.append(
                "{}{}".format("https://www.mariecallenders.com/locations", a["href"])
            )
        return res

    def retrieveStores(link, res):
        s = bs4.BeautifulSoup(sgrequests.SgRequests().get(link).text, features="lxml")
        for addr in s.findAll("address"):
            a = addr.find("a", href=True)
            res.append("{}{}".format("https://www.mariecallenders.com/", a["href"]))
        return res

    def retrieveStore(link):
        return bs4.BeautifulSoup(
            sgrequests.SgRequests().get(link).text, features="lxml"
        )

    states = retrieveStates()

    storeArr = []

    for state in states:
        retrieveStores(state, storeArr)

    result = []

    for stores in storeArr:
        s = retrieveStore(stores)
        name = s.find("title").text
        street = s.find("span", {"itemprop": "streetAddress"}).text
        city = s.find("span", {"itemprop": "addressLocality"}).text
        state = s.find("span", {"itemprop": "addressRegion"}).text
        zp = s.find("span", {"itemprop": "postalCode"}).text
        phone = s.find("span", {"itemprop": "telephone"}).text
        datetime = s.find("dt", {"itemprop": "openingHours"})["datetime"]
        timeArray = []
        for el in datetime.split("<br />"):
            if "am" in el or "pm" in el:
                timeArray.append(
                    el.strip()
                    .replace("Dining Room Now Open:", "")
                    .replace(u"\n", "")
                    .strip()
                )
        hours = ", ".join(timeArray)

        result.append(
            [
                locator_domain,
                stores,
                name,
                street,
                city,
                state,
                zp,
                missingString,
                missingString,
                phone,
                missingString,
                missingString,
                missingString,
                hours,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

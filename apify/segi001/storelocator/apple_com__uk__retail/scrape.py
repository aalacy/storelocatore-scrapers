import csv
import sgrequests
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
    locator_domain = "https://apple.com/uk/retail"
    missingString = "<MISSING>"

    def getUKStores():
        sess = sgrequests.SgRequests()
        return json.loads(sess.get("https://www.apple.com/today-bff/stores").text)[
            "en_GB"
        ]

    stores = getUKStores()

    result = []

    tA = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    def checkTime(t):
        return tA[t.index("Today")]

    for el in stores["stores"]:
        name = el["address"]["name"]
        city = el["address"]["city"]
        country = stores["countryTitle"]
        code = el["countryCode"]
        lat = el["lat"]
        lng = el["long"]
        store_num = el["storeNum"]
        s = bs4.BeautifulSoup(
            sgrequests.SgRequests().get(locator_domain + "/" + el["slug"]).text,
            features="lxml",
        )
        addr = s.find("address").get_text(separator="\n").strip().split("\n")
        addr.remove(",")
        addr.remove(" ")
        street = addr[0]
        zp = addr[-2]
        phone = addr[-1]
        hours = missingString
        timeArr = []
        loc_type = missingString
        dayTimes = []
        for e in s.findAll("tr"):
            if not e.find("td", {"class": "store-open-hours-day"}):
                pass
            else:
                dayTimes.append(e.find("td", {"class": "store-open-hours-day"}).text)
                timeArr.append(
                    "{} : {}".format(
                        e.find("td", {"class": "store-open-hours-day"}).text,
                        e.find("td", {"class": "store-open-hours-span"})
                        .text.strip()
                        .replace("*", "")
                        .replace("–", "-")
                        .replace(u"\xa0", u""),
                    )
                )
        hours = ", ".join(timeArr)
        if hours == "":
            hours = missingString
        hours = hours.replace("Today", checkTime(dayTimes))
        result.append(
            [
                locator_domain,
                locator_domain + "/" + el["slug"],
                name,
                street,
                city,
                country,
                zp,
                code,
                store_num,
                phone,
                loc_type,
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

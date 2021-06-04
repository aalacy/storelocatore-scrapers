import csv
import sgrequests
import json
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
    locator_domain = "https://apple.com/uk/retail"
    missingString = "<MISSING>"

    def getUKStores():
        sess = sgrequests.SgRequests()
        return json.loads(sess.get("https://www.apple.com/today-bff/stores").text)[
            "en_GB"
        ]

    stores = getUKStores()

    result = []

    tA = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu", "Fri"]

    def checkTime(t):
        return re.findall("[A-Z][^A-Z]*", tA[t.index("Today")])[0]

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
        for e in s.find("div", {"class": "store-hours"}):
            if not e.find("span", {"class": "visuallyhidden"}):
                pass
            else:
                for tr in e.find("tbody"):
                    dayTimes.append(tr.find("span", {"aria-hidden": "true"}).text)
                    timeArr.append(
                        "{} : {}".format(
                            tr.find("td", {"class": "store-hours-table-day"}).text,
                            tr.find("td", {"class": "store-hours-table-hours"})
                            .text.strip()
                            .replace("*", "")
                            .replace("–", "-")
                            .replace(u"\xa0", u""),
                        )
                    )
        hours = ", ".join(timeArr)
        if hours == "":
            hours = missingString
        hours = (
            hours.replace("Today", "TODAY", 1)
            .replace("TODAY", checkTime(dayTimes))
            .replace("Monday", "")
            .replace("Tuesday", "")
            .replace("Wednesday", "")
            .replace("Thursday", "")
            .replace("Friday", "")
            .replace("Saturday", "")
            .replace("Sunday", "")
            .replace("Today", "")
        )
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

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
        addr = s.findAll("p", {"class": "hcard-address"})[0].text
        zp = (
            s.findAll("p", {"class": "hcard-address"})[-2]
            .text.replace(city, "")
            .replace(",", "")
        )
        phone = s.findAll("p", {"class": "hcard-address"})[-1].text
        hours = missingString
        timeArr = []
        loc_type = missingString
        if (
            "We’re temporarily closed."
            in s.find(
                "div", {"class": "special-message typography-intro-elevated"}
            ).text
        ):
            hours = missingString
            loc_type = "Temporarily closed"
        else:
            for e in s.findAll("tr", {"class": "store-hours-line"}):
                timeArr.append(
                    "{} : {}".format(
                        e.find("td", {"class": "store-hours-day"}).text,
                        e.find("td", {"class": "store-hours-time"}).text,
                    )
                )
            hours = ", ".join(timeArr)

        result.append(
            [
                locator_domain,
                locator_domain + "/" + el["slug"],
                name,
                addr,
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

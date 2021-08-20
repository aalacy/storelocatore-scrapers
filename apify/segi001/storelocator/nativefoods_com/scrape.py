import csv
import sgrequests
import bs4


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    locator_domain = "https://nativefoods.com/"
    missingString = "<MISSING>"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initSoup(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    def retrieveStores():
        s = initSoup("https://nativefoods.com/")
        res = []
        for a in s.findAll("a", href=True):
            if "/locations/" in a["href"]:
                res.append("https://nativefoods.com" + a["href"])
        return list(set(res))

    stores = retrieveStores()

    result = []

    for store in stores:
        s = initSoup(store)
        url = store
        container = s.findAll("div", {"class": "map-details"})
        for c in container:
            name = c.find("div", {"class": "title"}).text
            street = c.find("p", {"class": "line1"}).text.strip()
            city = c.find("p", {"class": "line2"}).text.split(",")[0].strip()
            state = (
                c.find("p", {"class": "line2"})
                .text.split(",")[1]
                .strip()
                .split(" ")[0]
                .strip()
            )
            zp = (
                c.find("p", {"class": "line2"})
                .text.split(",")[1]
                .strip()
                .split(" ")[1]
                .strip()
            )
            h = c.findAll("p", {"class": "hours"})
            hours = missingString
            timeArr = []
            for hh in h:
                timeArr.append(hh.text.replace("Hours:", "").strip())
            hours = ", ".join(timeArr)
            phone = (
                c.find("p", {"class": "phone"})
                .text.strip()
                .replace("(", "")
                .replace(")", "")
                .strip()
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

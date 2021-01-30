import csv
import sgrequests
import bs4


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8") as output_file:
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
    locator_domain = "https://doublebees.com/"
    missingString = "<MISSING>"

    def getStores():
        def getAllStores():
            s = bs4.BeautifulSoup(
                sgrequests.SgRequests()
                .get(
                    "https://doublebees.com/wp-sitemap-posts-stores-1.xml",
                    headers={
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
                    },
                )
                .text,
                features="lxml",
            )
            res = []
            for loc in s.findAll("loc"):
                res.append(loc.text)
            return res

        store = getAllStores()

        res = []

        for s in store:
            soup = bs4.BeautifulSoup(
                sgrequests.SgRequests().get(s).text, features="lxml"
            )
            name = soup.find("div", {"class": "store-title"}).text
            addr = soup.find("div", {"class": "address fl"})
            street = addr.findAll("div")[0].text
            city = addr.findAll("div")[1].text.strip().split(u"\n")[0]
            state = addr.findAll("div")[1].text.split(u"\n")[2].strip().split(" ")[0]
            zp = addr.findAll("div")[1].text.split(u"\n")[2].strip().split(" ")[-1]
            if s == "https://doublebees.com/stores/conoco-store-136/":
                zp = missingString
                phone = (
                    addr.findAll("div")[1].text.split(u"\n")[2].strip().split(" ")[-2]
                    + addr.findAll("div")[1].text.split(u"\n")[2].strip().split(" ")[-1]
                )
            else:
                phone = soup.find("div", {"class": "contact-number fr"}).find("a").text
            latlng = (
                soup.find("div", {"class": "get-directions fl"})
                .find("a")["href"]
                .replace("https://www.google.com/maps/dir/Current+Location/", "")
            )
            lat = latlng.split(",")[0]
            lng = latlng.split(",")[1]
            timeArray = []
            for day in soup.findAll("span", {"class": "day"}):
                timeArray.append("{} : {}".format(day.text, day.find_next("span").text))
            hours = ", ".join(timeArray)
            if "24 Hour" in hours:
                hours = "24 Hours"
            res.append(
                {
                    "locator_domain": locator_domain,
                    "page_url": s,
                    "location_name": name,
                    "street_address": street,
                    "city": city.strip(),
                    "state": state,
                    "zip": zp,
                    "country_code": missingString,
                    "store_number": missingString,
                    "phone": phone.replace("(", "").replace(")", ""),
                    "location_type": missingString,
                    "latitude": lat,
                    "longitude": lng,
                    "hours": hours,
                }
            )
        return res

    stores = getStores()

    result = []

    for store in stores:
        result.append(
            [
                store["locator_domain"],
                store["page_url"],
                store["location_name"].strip(),
                store["street_address"],
                store["city"],
                store["state"],
                store["zip"],
                store["country_code"],
                store["store_number"],
                store["phone"],
                store["location_type"],
                store["latitude"],
                store["longitude"],
                store["hours"],
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

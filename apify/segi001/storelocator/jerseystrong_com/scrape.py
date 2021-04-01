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
    locator_domain = "https://jerseystrong.com/"
    missingString = "<MISSING>"

    def req(l):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"
        }
        return sgrequests.SgRequests().get(l, headers=headers)

    def initSoup(l):
        return bs4.BeautifulSoup(req(l).text, features="lxml")

    def retrieveStores():
        s = initSoup("https://jerseystrong.com/location-sitemap.xml")
        res = []
        for loc in s.findAll("loc"):
            if "/location/" in loc.text:
                res.append(loc.text)
        return res

    stores = retrieveStores()

    result = []

    for store in stores:
        s = initSoup(store)
        m = (
            s.find("div", {"class": "fl-rich-text"})
            .get_text()
            .strip()
            .replace("Jersey Strong Location:", "")
            .replace("Phone:", "")
            .strip()
            .replace("\xa0", "")
            .strip()
            .split("   ")
        )
        p = s.findAll("p")
        tA = []
        url = store
        name = s.find("span", {"class": "fl-heading-text"}).text.strip()
        phone = m[1]
        street = m[0].split(",")[0].strip()
        city = m[0].split(",")[1].strip()
        state = m[0].split(",")[2].strip().split(" ")[0].strip()
        zp = m[0].split(",")[2].strip().split(" ")[1].strip()
        for ps in p:
            if "Mon" in ps.text:
                tA.append(ps.text.replace("–", "-"))
        hours = "".join(tA)
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

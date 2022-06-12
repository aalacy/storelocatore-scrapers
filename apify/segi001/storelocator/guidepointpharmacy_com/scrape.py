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
    missingString = "<MISSING>"
    locator_domain = "https://www.guidepointpharmacyrx.com/"

    def req(l):
        return sgrequests.SgRequests().get(l)

    def initSoup(l):
        r = req(l)
        return bs4.BeautifulSoup(r.text, features="lxml")

    def retrieveStores():
        s = initSoup("https://www.guidepointpharmacyrx.com/sitemap.xml")
        res = []
        for loc in s.findAll("loc"):
            if "locations" in loc.text:
                if loc.text == "https://www.guidepointpharmacyrx.com/locations":
                    pass
                else:
                    res.append(loc.text)
        return res

    stores = retrieveStores()

    result = []

    for store in stores:
        s = initSoup(store)
        container_marker = s.findAll("div", {"class": "item itemPreview"})
        containers = {
            "location": container_marker[0]
            .find("div", {"class": "itemInnerContent"})
            .get_text(separator="/")
            .strip(),
            "phone": container_marker[1].find("li").text.strip().replace("Phone: ", ""),
            "hours": container_marker[2]
            .find("ul", {"class": "unstyledList"})
            .get_text(separator=" ")
            .strip(),
        }
        slash_split = containers["location"].split("/")
        name = (
            store.replace("https://www.guidepointpharmacyrx.com/locations/", "")
            .replace("-", " ")
            .title()
        )
        street = missingString
        city = missingString
        zp = missingString
        state = missingString
        phone = containers["phone"]
        hours = containers["hours"]
        url = store
        if "Coming Soon" in containers["hours"]:
            hours = missingString
        if len(slash_split) == 2:
            street = slash_split[0]
            if len(slash_split[1].split(",")) == 2:
                city = slash_split[1].split(",")[0]
                state = slash_split[1].split(",")[1].strip().split(" ")[0]
                zp = slash_split[1].split(",")[1].strip().split(" ")[1]
            else:
                city = slash_split[1].split(",")[0]
                state = slash_split[1].split(",")[1]
                zp = slash_split[1].split(",")[2]
        if len(slash_split) >= 3:
            street = slash_split[0]
            city = slash_split[1].split(",")[0]
            state = slash_split[1].split(",")[1]
            zp = slash_split[-1]
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

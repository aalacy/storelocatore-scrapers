import csv
import json
import bs4
import req


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
    TIMEOUT = 6
    locator_domain = "https://mountainsidefitness.com/"
    missingString = "<MISSING>"

    def createRequest(link):
        r = req.Req()
        r.setTimeout(TIMEOUT)
        return r.get(link)

    def initSoup(link):
        d = createRequest(link)
        return {
            "bs4": bs4.BeautifulSoup(d.text, features="lxml"),
            "status": d.status_code,
        }

    def returnAllStoreLinks():
        r = []
        for el in initSoup("https://mountainsidefitness.com/locations-sitemap.xml")[
            "bs4"
        ].findAll("loc"):
            r.append(el.text.strip())
        return r

    linkArray = returnAllStoreLinks()

    def sortLocations(j, arr):
        if j["url"] == "":
            pass
        else:
            storeNum = j["@id"]
            if j["@id"] == "":
                storeNum = missingString
            timeArray = []
            for e in j["openingHoursSpecification"]:
                if isinstance(e["dayOfWeek"], str):
                    timeArray.append(
                        e["dayOfWeek"] + " : " + e["opens"] + " - " + e["closes"]
                    )
                else:
                    for ele in e["dayOfWeek"]:
                        timeArray.append(ele + " : " + e["opens"] + " - " + e["closes"])
            hours = ", ".join(timeArray)
            arr.append(
                [
                    locator_domain,
                    j["url"],
                    j["name"],
                    j["address"]["streetAddress"],
                    j["address"]["addressLocality"],
                    j["address"]["addressRegion"],
                    j["address"]["postalCode"],
                    j["address"]["addressCountry"],
                    storeNum,
                    j["telephone"],
                    j["@type"],
                    j["geo"]["latitude"],
                    j["geo"]["longitude"],
                    hours,
                ]
            )

    result = []

    for link in linkArray:
        s = initSoup(link)
        if len(s["bs4"].findAll("script", {"type": "application/ld+json"})) == 1:
            pass
        else:
            ldjs = json.loads(
                str(s["bs4"].findAll("script", {"type": "application/ld+json"})[1])
                .replace('<script type="application/ld+json">', "")
                .replace("</script>", "")
            )
            sortLocations(ldjs, result)
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

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
    locator_domain = "https://www.communityamerica.com/"
    missingString = "<MISSING>"

    def getAllStores():
        api = "https://www.communityamerica.com/raytown-hyvee"
        call = sgrequests.SgRequests().get(api).text
        s = bs4.BeautifulSoup(call, features="lxml").findAll(
            "script", {"type": "application/ld+json"}
        )
        res = []
        for e in s:
            js = json.loads(
                str(e)
                .replace('<script type="application/ld+json">', "")
                .replace("</script>", "")
            )
            if js["@type"] == "BankOrCreditUnion":
                url = missingString
                for el in bs4.BeautifulSoup(
                    sgrequests.SgRequests()
                    .get(
                        "https://www.communityamerica.com/site/ajax/location_search.php?lat=39.0997265&long=-94.5785667&sur=0&coop=0&cacu=1"
                    )
                    .text,
                    features="lxml",
                ).findAll("div", {"class": "location cacu"}):
                    slug = el.find("div", {"class": "title"}).find("a", href=True)
                    if slug.text in js["name"]:
                        url = js["url"] + slug["href"]
                hours = missingString
                if "openingHours" in js:
                    hours = ", ".join(js["openingHours"])
                if "CommunityAmerica – Trans Air Branch" in js["name"]:
                    url = "https://www.communityamerica.com/trans-air"
                timeArray = []
                if (
                    "https://www.communityamerica.com/raytown-hyvee" in url
                    or "https://www.communityamerica.com/englewood-hyvee" in url
                ):
                    tbody = (
                        bs4.BeautifulSoup(
                            sgrequests.SgRequests().get(url).text, features="lxml"
                        )
                        .find("table")
                        .findAll("tbody")[0]
                        .findAll("tr")
                    )
                    day = ""
                    hours = ""
                    for el in tbody:
                        day = el.find("td", {"scope": "row"}).text.strip()
                        hours = el.findAll("td")[1].text.strip()
                        timeArray.append("{} : {}".format(day, hours))
                    hours = ", ".join(timeArray)
                res.append(
                    [
                        locator_domain,
                        url,
                        js["name"],
                        js["address"]["streetAddress"],
                        js["address"]["addressLocality"],
                        js["address"]["addressRegion"],
                        js["address"]["postalCode"],
                        missingString,
                        missingString,
                        js["telephone"],
                        missingString,
                        js["geo"]["latitude"],
                        js["geo"]["longitude"],
                        hours,
                    ]
                )
        return res

    result = getAllStores()

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

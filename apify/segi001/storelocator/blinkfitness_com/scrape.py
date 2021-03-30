import csv
from sgrequests import SgRequests
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
    sitemap = "https://locations.blinkfitness.com/sitemap.xml"
    site = "https://locations.blinkfitness.com"
    missingString = "<MISSING>"

    s = SgRequests()

    html = s.get(sitemap).text
    soup = bs4.BeautifulSoup(html, features="lxml")

    loc = soup.findAll("loc")

    result = []

    def removeDuplicates(arr):
        res = []
        for i in arr:
            if i not in res:
                res.append(i)
        return res

    for locs in loc:
        locsCheck = locs.text.replace(site, "").split("/")
        if len(locsCheck) == 2:
            pass
        else:
            s2 = SgRequests()
            html2 = s2.get(locs.text).text
            soup2 = bs4.BeautifulSoup(html2, features="lxml")
            name = "{} {}".format(
                soup2.findAll("span", {"class": "LocationName-brand"})[0].text,
                soup2.findAll("span", {"class": "LocationName-geo"})[0].text,
            )
            street = soup2.findAll("span", {"class": "c-address-street-1"})[0].text
            city = soup2.findAll("span", {"class": "c-address-city"})[0].text
            state = soup2.findAll("abbr", {"class": "c-address-state"})[0].text
            zipC = soup2.findAll("span", {"class": "c-address-postal-code"})[0].text
            phone = soup2.findAll("a", {"class": "Phone-link"})[0].text
            hOfOpArray = soup2.findAll("tr", {"itemprop": "openingHours"})
            hOfOpCollector = []
            for el in hOfOpArray:
                day = ""
                if "Mo" in el["content"]:
                    day = "Monday"
                elif "Tu" in el["content"]:
                    day = "Tuesday"
                elif "We" in el["content"]:
                    day = "Wednesday"
                elif "Th" in el["content"]:
                    day = "Thursday"
                elif "Fr" in el["content"]:
                    day = "Friday"
                elif "Sa" in el["content"]:
                    day = "Saturday"
                elif "Su" in el["content"]:
                    day = "Sunday"
                hours = el["content"].split(" ")
                hOfOpCollector.append("{} : {}".format(day, hours[1]))

            parsedList = removeDuplicates(hOfOpCollector)
            hours_of_operation = ", ".join(str(x) for x in parsedList)

            result.append(
                [
                    site,
                    locs.text,
                    name,
                    street,
                    city,
                    state,
                    zipC,
                    missingString,
                    missingString,
                    phone,
                    missingString,
                    missingString,
                    missingString,
                    hours_of_operation,
                ]
            )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

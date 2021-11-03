import csv
import sgrequests
import json
import re
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
    locator_domain = "https://community.petsathome.com/"
    missingString = "<MISSING>"

    def getAllStores():
        url = (
            sgrequests.SgRequests()
            .get("https://www.petsathomejobs.com/retail-jobs/locations")
            .text
        )
        js = json.loads(re.search(r"var locations = (.*?);", url).group(1))
        res = []
        for el in js:
            u = "https://community.petsathome.com/store/{}/".format(el["title"])
            s = bs4.BeautifulSoup(
                sgrequests.SgRequests().get(u).text, features="lxml"
            ).findAll("div", {"class": "collapsible-body no-grid-spacing"})
            timeArray = []
            hours = missingString
            if len(s) < 1:
                hours = missingString
            else:
                new = list(filter(None, s[1].text.split("\n")))
                while "—" in new:
                    new.remove("—")
                for ee in list(zip(*[iter(new)] * 3)):
                    timeArray.append("{} : {} - {}".format(ee[0], ee[1], ee[2]))
                hours = ", ".join(timeArray)
            if hours == "":
                hours = missingString
            phone = el["telephone"]
            if phone == "":
                phone = missingString
            lat = el["latitude"]
            lng = el["longitude"]
            if lat == "":
                lat = missingString
            if lng == "":
                lng = missingString
            res.append(
                [
                    locator_domain,
                    u,
                    el["title"],
                    el["address"]
                    .replace(",", " ")
                    .replace(el["address"].split(",")[-2], "")
                    .replace(el["address"].split(",")[-1], "")
                    .strip(),
                    el["address"].split(",")[-2].strip(),
                    missingString,
                    el["address"].split(",")[-1].strip(),
                    missingString,
                    el["id"],
                    phone,
                    missingString,
                    lat,
                    lng,
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

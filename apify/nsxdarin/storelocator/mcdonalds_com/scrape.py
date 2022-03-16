import csv
from sgrequests import SgRequests
import json


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    session = SgRequests()
    url = "https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=40.0&longitude=-95.0&radius=20000&maxResults=30000&country=us&language=en-us&showClosed=&hours24Text=Open%2024%20hr"

    headers = {
        "Host": "www.mcdonalds.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0",
        "Accept": "*/*",
        "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://www.mcdonalds.com/us/en-us/restaurant-locator.html",
    }

    r = session.get(url, headers=headers, timeout=90, stream=True, verify=False)
    array = json.loads(r.content)

    country = "US"
    website = "mcdonalds.com"
    typ = "Restaurant"

    for item in array["features"]:
        store = item["properties"]["identifierValue"]
        page_url = f"https://www.mcdonalds.com/us/en-us/location/{store}.html"
        add = item["properties"]["addressLine1"]
        add = add.strip()
        city = item["properties"]["addressLine3"]
        state = item["properties"]["subDivision"]
        zc = item["properties"]["postcode"]
        try:
            phone = item["properties"]["telephone"]
        except:
            phone = "<MISSING>"
        name = "McDonald's # " + store
        lat = item["geometry"]["coordinates"][0]
        lng = item["geometry"]["coordinates"][1]
        try:
            hours = "Mon: " + item["properties"]["restauranthours"]["hoursMonday"]
            hours = (
                hours
                + "; Tue: "
                + item["properties"]["restauranthours"]["hoursTuesday"]
            )
            hours = (
                hours
                + "; Wed: "
                + item["properties"]["restauranthours"]["hoursWednesday"]
            )
            hours = (
                hours
                + "; Thu: "
                + item["properties"]["restauranthours"]["hoursThursday"]
            )
            hours = (
                hours + "; Fri: " + item["properties"]["restauranthours"]["hoursFriday"]
            )
            hours = (
                hours
                + "; Sat: "
                + item["properties"]["restauranthours"]["hoursSaturday"]
            )
            hours = (
                hours + "; Sun: " + item["properties"]["restauranthours"]["hoursSunday"]
            )
        except:
            hours = "<MISSING>"
        if "Maharastra" not in state:
            yield [
                website,
                page_url,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours,
            ]


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

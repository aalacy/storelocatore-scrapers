import csv
import sgrequests
import json


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
    url = "https://www.goldenkrust.com/"
    api = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/6066/stores.js?callback=SMcallback2:formatted"
    missingString = "<MISSING>"

    st = json.loads(
        sgrequests.SgRequests().get(api).text.replace("SMcallback2:formatted", "")[1:-1]
    )
    result = []
    for s in st["stores"]:
        name = s["name"]
        address = s["address"].split(",")[0]
        city = s["address"].split(",")[1]
        state = s["address"].split(",")[2].split(" ")[1]
        zipc = ""
        if len(s["address"].split(",")[2].split(" ")) == 3:
            zipc = s["address"].split(",")[2].split(" ")[2]
        else:
            zipc = s["address"].split(",")[3]
        if "USA" in zipc:
            zipc = missingString
        phone = ""
        if s["phone"]:
            phone = s["phone"]
        else:
            phone = missingString
        lat = s["latitude"]
        lng = s["longitude"]
        result.append(
            [
                url,
                missingString,
                name,
                address,
                city,
                state,
                zipc,
                missingString,
                missingString,
                phone,
                missingString,
                lat,
                lng,
                missingString,
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

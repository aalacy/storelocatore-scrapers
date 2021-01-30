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
    locator_domain = "https://figaros.com/"
    missingString = "<MISSING>"

    def getStores():
        api = "https://figaros.com/modules/multilocation/?near_location=Mexico&services__in=&published=1&within_business=true&offset=0&limit=1000"
        jsonPacket = json.loads(
            sgrequests.SgRequests()
            .get(
                api,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
                },
            )
            .text
        )
        res = []
        for e in jsonPacket["objects"]:
            name = e["location_name"]
            page = e["location_url"]
            street = e["street"]
            if e["street2"]:
                street = e["street"] + " " + e["street2"]
            city = e["city"]
            state = e["state"]
            zp = e["postal_code"]
            code = e["country"]
            store_num = e["id"]
            phone = e["phonemap"]["phone"]
            lat = e["lat"]
            lng = e["lon"]
            timeArray = []
            for days in e["formatted_hours"]["primary"]["days"]:
                timeArray.append("{} : {}".format(days["label"], days["content"]))
            hours = ", ".join(timeArray)
            res.append(
                {
                    "locator_domain": locator_domain,
                    "page": page,
                    "name": name,
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zp,
                    "code": code,
                    "num": store_num,
                    "phone": phone,
                    "type": missingString,
                    "lat": lat,
                    "lng": lng,
                    "hours": hours,
                }
            )
        return res

    result = []

    for s in getStores():
        result.append(
            [
                s["locator_domain"],
                s["page"],
                s["name"],
                s["street"],
                s["city"],
                s["state"],
                s["zip"],
                s["code"],
                s["num"],
                s["phone"],
                s["type"],
                s["lat"],
                s["lng"],
                s["hours"],
            ]
        )
    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

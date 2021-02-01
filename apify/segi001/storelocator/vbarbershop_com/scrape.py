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
    locator_domain = "https://vbarbershop.com/"
    api = "https://api2.storepoint.co/v1/15e4d951aa1fce/locations?rq"
    missingString = "<MISSING>"

    sess = sgrequests.SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
    }

    req = json.loads(sess.get(api, headers=headers).text)

    result = []

    for s in req["results"]["locations"]:
        state = s["streetaddress"].split(",")[-1].split(" ")[-2].strip()
        zc = s["streetaddress"].split(",")[-1].split(" ")[-1].strip()
        city = s["streetaddress"].split(",")[-2].strip()
        phone = s["phone"]
        location_type = missingString

        hours = ", ".join(
            [
                f"Monday : {s['monday']}",
                f"Tuesday : {s['tuesday']}",
                f"Wednesday : {s['wednesday']}",
                f"Thursday : {s['thursday']}",
                f"Friday : {s['friday']}",
                f"Saturday : {s['saturday']}",
                f"Sunday : {s['sunday']}",
            ]
        )

        if "COMING SOON" in s["tags"]:
            hours = missingString
            phone = missingString
            location_type = "Coming Soon"

        if zc == "FL":
            zc = missingString
            state = s["streetaddress"].split(",")[-1].split(" ")[-1].strip()

        street = (
            s["streetaddress"]
            .replace(",", "")
            .replace(state, "")
            .replace(city, "")
            .replace(zc, "")
            .strip()
            .replace("* MAIL ADDRESS DIFFERENT", "")
        )

        result.append(
            [
                locator_domain,
                s["website"],
                s["name"],
                street,
                city,
                state,
                zc,
                missingString,
                missingString,
                phone,
                location_type,
                s["loc_lat"],
                s["loc_long"],
                hours,
            ]
        )

    return result


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

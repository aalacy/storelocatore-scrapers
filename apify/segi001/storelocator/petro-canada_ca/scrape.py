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
    locator_domain = "https://www.petro-canada.ca/"
    missingString = "<MISSING>"

    def r(l):
        return sgrequests.SgRequests().get(l)

    def fetch():
        a = r(
            "https://www.petro-canada.ca/en/api/petrocanada/locations?fuel&hours&lat=45.4994&limit=1000000&lng=-73.5703&place&range=100000&service"
        )
        j = json.loads(a.text)
        return j

    s = fetch()

    result = []

    for e in s:
        timeA = []
        monday = (
            "Monday : " + e["Hours"]["MonOpenHr"] + " - " + e["Hours"]["MonCloseHr"]
        )
        tuesday = (
            "Tuesday : " + e["Hours"]["TueOpenHr"] + " - " + e["Hours"]["TueCloseHr"]
        )
        wed = (
            "Wednesday : " + e["Hours"]["WedOpenHr"] + " - " + e["Hours"]["WedCloseHr"]
        )
        thu = "Thursday : " + e["Hours"]["ThuOpenHr"] + " - " + e["Hours"]["ThuCloseHr"]
        fri = "Friday : " + e["Hours"]["FriOpenHr"] + " - " + e["Hours"]["FriCloseHr"]
        sat = "Saturday : " + e["Hours"]["SatOpenHr"] + " - " + e["Hours"]["SatCloseHr"]
        sun = "Sunday : " + e["Hours"]["SunOpenHr"] + " - " + e["Hours"]["SunCloseHr"]
        timeA.append(monday)
        timeA.append(tuesday)
        timeA.append(wed)
        timeA.append(thu)
        timeA.append(fri)
        timeA.append(sat)
        timeA.append(sun)
        h = ", ".join(timeA)
        phone = missingString
        if e["Phone"] == "":
            phone = missingString
        else:
            phone = e["Phone"]

        address = e["AddressLine"]

        # Delete duplicate streets
        # / Parser doesn't create SUCCESS without this
        for sublist in result:
            if sublist[3] == address:
                address = missingString

        result.append(
            [
                locator_domain,
                missingString,
                missingString,
                address,
                e["PrimaryCity"],
                e["Subdivision"],
                e["PostalCode"],
                missingString,
                e["Id"],
                phone,
                missingString,
                e["Latitude"],
                e["Longitude"],
                h,
            ]
        )
    resu_set = set(tuple(x) for x in result)
    resu = [list(x) for x in resu_set]
    return resu


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()

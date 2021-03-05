import csv
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


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
    data = []
    url = "https://www.zpizza.com/locations"
    p = 0
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split(
        '"galleryImages":[],"giftCardImages":[],"giftCardShopItem":null,"locations":'
    )[3].split(',"socialHandles":[]}],"menus":[]', 1)[0]
    r = r + ',"socialHandles":[]}]'
    loclist = json.loads(r)
    for loc in loclist:
        store = loc["id"]
        state = loc["state"]
        city = loc["city"]
        ccode = loc["country"]
        pcode = loc["postalCode"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["streetAddress"]
        hourlist = loc["schemaHours"]
        title = loc["name"]
        link = "https://www.zpizza.com/" + loc["slug"]
        if link.find("bend-tap-room") > -1:
            link = link.split("-")[0]
        phone = (
            loc["phone"][0:3]
            + "-"
            + loc["phone"][3:6]
            + "-"
            + loc["phone"][6 : len(loc["phone"])]
        )
        hours = ""
        hourd = []
        hourd.append("none")
        try:
            for hr in hourlist:
                dt = hr.split(" ", 1)[0]
                if dt in hourd:
                    pass
                else:
                    hourd.append(dt)
                    day = (int)(hr.split("-")[1].split(":")[0])
                    if day > 12:
                        day = day - 12
                    hours = (
                        hours + hr.split("-")[0] + " am " + " - " + str(day) + ":00 PM"
                    )
                    hours = hours + " "
            hours = (
                hours.replace("Su", "Sunday")
                .replace("Mo", "Monday")
                .replace("Tu", "Tuesday")
                .replace("We", "Wednesday")
                .replace("Th", "Thursday")
                .replace("Fr", "Friday")
                .replace("Sa", "Saturday")
            )
        except:
            hours = "<MISSING>"
        data.append(
            [
                "https://www.zpizza.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                ccode,
                store,
                phone,
                "<MISSING>",
                lat,
                longt,
                hours,
            ]
        )

        p += 1
    return data


def scrape():

    data = fetch_data()
    write_output(data)


scrape()

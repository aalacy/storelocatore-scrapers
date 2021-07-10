import csv
import json
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "contentType": "application/json",
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
    url = "https://www.mynycb.com/api/async/branches"
    p = 0
    loclist = session.get(url, headers=headers, verify=False).json()
    loclist = json.loads(loclist)

    for loc in loclist:
        title = loc["Name"]
        store = loc["Services"][0]["LocationId"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        street = loc["AddressLine1"] + " " + str(loc["AddressLine2"])
        street = street.replace("None", "").strip()
        city = loc["City"]
        state = loc["StateCode"]
        pcode = loc["PostalCode"]
        ccode = "US"
        phone = loc["Phone"]
        hourslist = loc["LocationHours"]
        hours = ""
        for hr in hourslist:
            if "Branch Services" in hr["ServiceName"]:
                try:
                    start = (
                        hr["StartTime"].split(":")[0]
                        + ":"
                        + hr["StartTime"].split(":")[1]
                        + " AM - "
                    )
                    end = (int)(hr["EndTime"].split(":")[0])
                    if end > 12:
                        end = end - 12
                    endtime = str(end) + ":" + hr["EndTime"].split(":")[1] + " PM  "
                    hours = hours + hr["Weekday"] + " " + start + endtime
                except:
                    hours = hours + hr["Weekday"] + " Closed "
        if len(hours) < 3:
            hours = "<MISSING>"
        if "ATM" in loc["Type"]["Name"]:
            ltype = "ATM"
            hours = "<MISSING>"
            phone = "<MISSING>"
        else:
            ltype = "Branch"
        if title.find("Coming Soon") == -1:
            data.append(
                [
                    "https://www.mynycb.com/",
                    "https://www.mynycb.com/BranchLocator/Index",
                    title,
                    street,
                    city,
                    state,
                    pcode,
                    ccode,
                    store,
                    phone,
                    ltype,
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

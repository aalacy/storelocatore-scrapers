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
    p = 0
    data = []
    url = "https://www.campbowwow.com/locations/?CallAjax=GetLocations"
    loclist = session.get(url, headers=headers, verify=False).json()
    for loc in loclist:

        link = "https://www.campbowwow.com" + loc["Path"]
        store = loc["FranchiseLocationID"]
        title = loc["FranchiseLocationName"]
        street = loc["Address1"] + loc["Address2"]
        city = loc["City"]
        state = loc["State"]
        pcode = loc["ZipCode"]
        ccode = loc["Country"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        phone = loc["Phone"]
        if len(str(phone)) < 3:
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        else:
            phone = "<MISSING>"
        try:
            hourslist = loc["LocationHours"]
            hourslist = (
                hourslist.replace("]", "}").replace("[", "{").replace("}{", "},{")
            )
            hourslist = "[" + hourslist + "]"
            hourslist = json.loads(hourslist)

            hours = ""
            for hr in hourslist:
                day = hr["Interval"]
                if "Holiday" in day:
                    break
                start = hr["OpenTime"]
                end = hr["CloseTime"]
                st = (int)(start.split(":", 1)[0])
                if st > 12:
                    st = st - 12
                endst = (int)(end.split(":", 1)[0])
                if endst > 12:
                    endst = endst - 12
                hours = (
                    hours
                    + day
                    + " "
                    + str(st)
                    + ":"
                    + start.split(":")[1]
                    + " AM - "
                    + str(endst)
                    + ":"
                    + end.split(":")[1]
                    + " PM "
                )
        except:

            hours = "<MISSING>"
        data.append(
            [
                "https://www.campbowwow.com/",
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

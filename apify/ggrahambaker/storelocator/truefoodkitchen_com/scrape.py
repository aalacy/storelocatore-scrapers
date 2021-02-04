import csv
from sgrequests import SgRequests
import json

session = SgRequests()
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36"
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
    hours_map = {
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursday",
        "5": "Friday",
        "6": "Saturday",
        "7": "Sunday",
    }
    url = "https://www.truefoodkitchen.com/locations/"
    r = session.get(url, headers=HEADERS)
    loclist = r.text.split(" locations = ", 1)[1].split(";", 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        if "coming" in loc["status"] or "soon" in loc["status"]:
            continue
        link = loc["link"]
        r = session.get(link, headers=HEADERS)
        title = loc["title"]
        street = loc["street"]
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        phone = loc["phone"]
        coord = loc["geo"]
        lat = coord[0]
        longt = coord[1]
        loc_id = r.text.split("momentFeedID = '", 1)[1].split("';")[0]
        hourlink = (
            "https://api.momentfeed.com/v1/lf/location/store-info/"
            + loc_id
            + "?auth_token=IFWKRODYUFWLASDC"
        )
        r = session.get(hourlink, headers=HEADERS, verify=False).json()
        store = r["corporateId"]
        hourlist = r["hours"].split(";")
        hours = ""
        for hr in hourlist:
            temp = hr.split(",")
            if len(temp) == 1:
                continue
            day = hours_map[temp[0]]
            n = 2
            start = [temp[1][i : i + n] for i in range(0, len(temp[1]), n)]
            start1 = (int)(start[0])
            start2 = start[1]
            part = ""
            if start1 < 12:
                part = " am "
                pass
            else:
                start1 = start1 - 12
                part = " pm "
            startstr = str(start1) + " : " + start2 + " " + part
            n = 2
            end = [temp[2][i : i + n] for i in range(0, len(temp[2]), n)]
            end1 = (int)(end[0])
            end2 = end[1]
            part = ""
            if end1 < 12:
                part = " am "
                pass
            else:
                end1 = end1 - 12
                part = " pm "
            endstr = str(end1) + " : " + end2 + " " + part
            hours = hours + day + " " + startstr + "- " + endstr + " "
        if len(hours) < 3:
            hours = "<MISSING>"
        data.append(
            [
                "https://www.truefoodkitchen.com/",
                link,
                title,
                street,
                city,
                state,
                pcode,
                "US",
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

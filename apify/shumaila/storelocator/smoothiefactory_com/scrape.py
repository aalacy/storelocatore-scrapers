import csv
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
    p = 0
    url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=ZLHQWBGKROQFVIUG&page=1&pageSize=100"
    loclist = session.get(url, headers=headers, verify=False).json()
    hourd = {
        "1": "Mon",
        "2": "Tues",
        "3": "Wed",
        "4": "Thurs",
        "5": "Fri",
        "6": "Sat",
        "7": "Sun",
    }
    for loc1 in loclist:
        loc = loc1["store_info"]
        title = loc["name"]
        store = loc["corporate_id"]
        street = loc["address"]
        try:
            street = street + " " + loc["address_extended"]
        except:
            pass
        city = loc["locality"]
        state = loc["region"]
        pcode = loc["postcode"]
        phone = loc["phone"]
        if "(" not in phone:
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        lat = loc["latitude"]
        longt = loc["longitude"]
        hourlist = loc["store_hours"].split(";")
        hours = ""
        for hr in hourlist:
            try:
                day, start, end = hr.split(",")
                day = hourd[str(day)]
                start1 = str(start)[0:2]
                start2 = str(start)[2:]
                end1 = (int)(str(end)[0:2])
                end2 = str(end)[2:]
                if end1 > 12:
                    end1 = end1 - 12
                hours = (
                    hours
                    + day
                    + " "
                    + start1
                    + ":"
                    + start2
                    + " AM - "
                    + str(end1)
                    + ":"
                    + str(end2)
                    + " PM "
                )
            except:
                pass
        link = "https://locations.smoothiefactory.com" + loc1["llp_url"]
        if "coming soon" in loc1["open_or_closed"]:
            continue
        if len(hours) < 3:
            hours = "Temporarily Closed"
        data.append(
            [
                "https://smoothiefactory.com/",
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

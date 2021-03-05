import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "authority": "api-web.rxwiki.com",
    "method": "POST",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-length": "96",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://api-web.rxwiki.com",
    "referer": "https://api-web.rxwiki.com/find-a-pharmacy/?maxHeight=590&maxWidth=1518&appId=14308e3e-f77d-4c38-8ece-c8449b8f8e66",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "DC",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
    ]
    streetlist = []
    data = []
    daylist = {
        "1": "Monday",
        "2": "Tuesday",
        "3": "Wednesday",
        "4": "Thursday",
        "5": "Friday",
        "6": "Saturday",
    }
    url = "https://api-web.rxwiki.com/api/v2/location/search"
    for statenow in states:

        myobj = {
            "search_radius": 1000,
            "query": statenow,
            "page": 1,
            "app_id": "14308e3e-f77d-4c38-8ece-c8449b8f8e66",
        }
        loclist = session.post(url, headers=headers, json=myobj).json()["locations"]
        if len(loclist) == 0:

            continue
        for loc in loclist:
            city = str(loc["addr"]["Main"]["city"])
            ccode = str(loc["addr"]["Main"]["country"])
            pcode = str(loc["addr"]["Main"]["zip"])
            street = (
                str(loc["addr"]["Main"]["street1"])
                + " "
                + str(loc["addr"]["Main"]["street2"])
            )
            state = loc["addr"]["Main"]["state"]
            title = loc["displayName"]
            store = str(loc["id"])
            if street in streetlist:
                continue
            streetlist.append(street)
            lat = loc["latitude"]
            longt = loc["longitude"]
            link = loc["custUrl"]["Main"]["url"]
            hours = "Sunday Closed "
            hourslist = loc["hours"]
            phone = str(loc["phone"])
            phone = "(" + phone[0:3] + ") " + phone[3:6] + "-" + phone[6:10]
            for hr in hourslist:
                try:
                    day = daylist[str(hr["day"])]
                except:
                    pass
                if hr["endHH"] == 0:
                    continue
                endt1 = (int)(hr["endHH"])
                if endt1 > 12:
                    endt1 = endt1 - 12
                endt2 = hr["endMM"]
                if endt2 == 0:
                    endd = "00"
                else:
                    endd = str(endt2)
                start2 = (int)(hr["startMM"])
                if start2 == 0:
                    stt2 = str("00")
                else:
                    stt2 = str(start2)
                start = str(hr["startHH"]) + ":" + stt2 + " AM - "

                hours = hours + day + " " + start + str(endt1) + ":" + endd + " PM "
            if "Saturday" not in hours:
                hours = hours + " Saturday Closed"
            if len(link) < 3:
                link = "https://www.medicap.com/find-a-pharmacy"
            if "West Virginia" in state:
                state = "WV"
            if "Wyoming" in state:
                state = "WY"
            data.append(
                [
                    "https://www.medicap.com/",
                    link,
                    title,
                    street.replace(" None", ""),
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

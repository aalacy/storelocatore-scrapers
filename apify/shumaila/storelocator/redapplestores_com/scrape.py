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

    statelist = [
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NT",
        "NS",
        "NU",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ]
    data = []
    p = 0
    for state in statelist:
        url = (
            "https://www.redapplestores.com/ajax_store.cfm?province="
            + state
            + "&action=cities"
        )
        try:
            loclist = session.get(url, headers=headers, verify=False).json()["data"]
        except:
            continue
        for loc in loclist:
            link = "https://www.redapplestores.com" + loc["val"]
            r = session.get(link, headers=headers, verify=False)
            content = r.text.split('"locations":[', 1)[1].split("],", 1)[0]
            content = json.loads(content)
            ccode = content["country"]
            pcode = content["postalzip"]
            lat = content["lat"]
            longt = content["lon"]
            city = content["city"]
            phone = content["phone"]
            street = content["address"]
            hourlist = (
                r.text.split('"google_structured_data":"', 1)[1]
                .split('}"', 1)[0]
                .replace("\\", "")
                + "}"
            )
            hourlist = json.loads(hourlist)
            hourlist = hourlist["openingHoursSpecification"]
            hours = ""
            for hr in hourlist:
                day = hr["dayOfWeek"][0]
                opentime = hr["opens"]
                closetime = hr["closes"]
                close = (int)(closetime.split(":", 1)[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hours
                    + day
                    + " "
                    + opentime
                    + " AM - "
                    + str(close)
                    + ":"
                    + closetime.split(":", 1)[1]
                    + " PM "
                )
            title = "Red Apple - " + city + ", " + state.upper()
            store = link.split("/store/", 1)[1].split("/", 1)[0]
            data.append(
                [
                    "https://www.redapplestores.com",
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

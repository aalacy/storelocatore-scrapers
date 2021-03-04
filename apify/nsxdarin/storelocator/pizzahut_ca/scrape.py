import csv
from sgrequests import SgRequests
import datetime

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():
    url = "https://api.pizzahut.io/v1/huts/nearby?lat=45.621413&lon=-90.3788412&limit=2500&sectors=ca-1"
    r = session.get(url, headers=headers, timeout=60)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '","id":"' in line:
            items = line.split('","id":"')
            for item in items:
                if ',"name":"' in item:
                    website = "pizzahut.ca"
                    hours = ""
                    store = item.split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    addcount = (
                        item.split('"address":{"lines":["')[1]
                        .split('"],"region":')[0]
                        .count('","')
                    )
                    if addcount == 2:
                        add = item.split('"address":{"lines":["')[1].split('"')[0]
                    else:
                        add = (
                            item.split('"address":{"lines":["')[1].split('"')[0]
                            + " "
                            + item.split('"address":{"lines":["')[1].split('","')[1]
                        )
                    city = name
                    if " - " in city:
                        city = city.split(" - ")[0].strip()
                    state = item.split('"region":"')[1].split('"')[0]
                    country = "CA"
                    zc = item.split('"postcode":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    typ = "<MISSING>"
                    purl = "https://pizzahut.ca/huts/ca-1/" + store
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    hours = ""
                    hurl = (
                        "https://api.pizzahut.io/v1/hut?sector=ca-1&hutId="
                        + store
                        + "&openDays=7"
                    )
                    r2 = session.get(hurl, headers=headers)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
                        if '"hours":{"physical":' in line2:
                            days = (
                                line2.split('"hours":{"physical":')[1]
                                .split("}],")[0]
                                .split('{"disposition":"collection","open":"')
                            )
                            for day in days:
                                if '"close":"' in day:
                                    dt = day.split("T")[0]
                                    year, month, dday = (int(x) for x in dt.split("-"))
                                    ans = datetime.date(year, month, dday)
                                    weekday = ans.strftime("%A")
                                    hrs = (
                                        weekday
                                        + ": "
                                        + day.split("T")[1].split(":00-")[0]
                                        + "-"
                                        + day.split('"close":"')[1]
                                        .split("T")[1]
                                        .split(":00-")[0]
                                    )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                    if "(" in phone:
                        phone = "(" + phone.split("(")[1]
                    if "(" in add:
                        add = add.split("(")[0].strip()
                    if hours == "":
                        hours = "<MISSING>"
                    if phone != "5555555555":
                        yield [
                            website,
                            purl,
                            name,
                            add,
                            city,
                            state,
                            zc,
                            country,
                            store,
                            phone,
                            typ,
                            lat,
                            lng,
                            hours,
                        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

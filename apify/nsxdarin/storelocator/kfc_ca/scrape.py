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
    url = "https://www.kfc.ca/find-a-kfc"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '"RestaurantName":"' in line and "var allRestDetails" in line:
            items = line.split('"RestaurantName":"')
            for item in items:
                if "var allRestDetails" not in item and "TEST-CA" not in item:
                    name = "KFC"
                    try:
                        add = item.split('"AddressLine1":"')[1].split('"')[0]
                    except:
                        add = "<MISSING>"
                    if add != "<MISSING>":
                        try:
                            add2 = item.split('"AddressLine2":"')[1].split('"')[0]
                            add = add + " " + add2
                        except:
                            pass
                    add = add.strip()
                    store = item.split('"')[0]
                    try:
                        city = item.split('"City":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    try:
                        state = item.split('"Province":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    try:
                        zc = item.split('"PostalCode":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    country = "CA"
                    try:
                        phone = item.split('"PhoneNo":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        lat = item.split('"Lat":"')[1].split('"')[0]
                        lng = item.split('"Long":"')[1].split('"')[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    typ = "Restaurant"
                    website = "kfc.ca"
                    loc = (
                        "https://www.kfc.ca/store/"
                        + item.split('"AddressDisplyName":"')[1].split('"')[0]
                    )
                    hours = ""
                    if '"Hours":[]' in item:
                        hours = "<MISSING>"
                    else:
                        days = (
                            item.split('"Hours":[')[1]
                            .split("]")[0]
                            .split('"RestaurantId":"')
                        )
                        for day in days:
                            if '"Day":0' in day:
                                hours = (
                                    hours
                                    + "; Sun: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                            if '"Day":1' in day:
                                hours = (
                                    hours
                                    + "; Mon: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                            if '"Day":2' in day:
                                hours = (
                                    hours
                                    + "; Tue: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                            if '"Day":3' in day:
                                hours = (
                                    hours
                                    + "; Wed: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                            if '"Day":4' in day:
                                hours = (
                                    hours
                                    + "; Thu: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                            if '"Day":5' in day:
                                hours = (
                                    hours
                                    + "; Fri: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                            if '"Day":6' in day:
                                hours = (
                                    hours
                                    + "; Sat: "
                                    + day.split('"OpenTime":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"CloseTime":"')[1].split('"')[0]
                                )
                        hours = hours[2:]
                    if "n/a-n/a" in hours:
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    add = add.replace("\\u0027", "'").replace("\\u0026", "&")
                    yield [
                        website,
                        loc,
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

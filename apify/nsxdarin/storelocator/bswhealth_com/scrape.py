import csv
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-bsw-correlationid": "ecf2fb2f-89bb-41a6-bc53-68ffc5880f56",
    "x-bsw-sessionid": "ecf2fb2f-89bb-41a6-bc53-68ffc5880f56",
    "x-bsw-clientid": "BSWHealth.com",
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
    url = "https://phyndapi.bswapi.com/V2/Places/GetLocations?&location=37.912491449640854,-99.5631319&distance=2500&LineOfBusiness=BSWH&pageNumber=1&perPage=2500&SortBy=Distance&DocIsPrimaryCare=true&DocUsesMyBSWHealth=true&DocSortBy=NextAvailableAppointment&overrideRules=true"
    r = session.get(url, headers=headers, stream=True)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "bswhealth.com"
    for line in r.iter_lines(decode_unicode=True):
        if '"locationType":"' in line:
            items = line.split('"locationType":"')
            for item in items:
                if '"photoUrl":' in item:
                    typ = item.split('"')[0]
                    country = "US"
                    try:
                        loc = item.split('"locationUrl":"')[1].split('"')[0]
                    except:
                        loc = "<MISSING>"
                    if loc == "":
                        loc = "<MISSING>"
                    lat = item.split('"lat":')[1].split(",")[0]
                    lng = item.split('"lon":')[1].split("}")[0]
                    store = item.split('"locationID":"')[1].split('"')[0]
                    name = item.split('"locationName":"')[1].split('"')[0]
                    phone = item.split('"locationPhone":"')[1].split('"')[0]
                    state = item.split('"locationState":"')[1].split('"')[0]
                    add = item.split('"locationStreet1":"')[1].split('"')[0]
                    add = add + " " + item.split('"locationStreet2":"')[1].split('"')[0]
                    city = item.split('"locationCity":"')[1].split('"')[0]
                    zc = item.split('"locationZip":"')[1].split('"')[0]
                    add = add.strip()
                    hours = ""
                    if '"dailyHours":[]' not in item:
                        days = (
                            item.split('"dailyHours":[')[1]
                            .split("]")[0]
                            .split('"weekDayName":"')
                        )
                        for day in days:
                            if '"openingTime":"' in day:
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split('"openingTime":"')[1]
                                    .split('"')[0]
                                    .rsplit(":", 1)[0]
                                    + "-"
                                    + day.split('"closingTime":"')[1]
                                    .split('"')[0]
                                    .rsplit(":", 1)[0]
                                )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if " - " in name:
                        name = name.split(" - ")[0].strip()
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

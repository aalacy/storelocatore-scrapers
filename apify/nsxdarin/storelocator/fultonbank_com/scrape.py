import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

logger = SgLogSetup().get_logger("fultonbank_com")


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
    url = "https://www.fultonbank.com/api/Branches/Search"
    payload = {
        "QueryModel.SearchTerm": "10001",
        "QueryModel.AmenityIds": "{825980DA-DD13-445E-B9EB-C9B521B918C2}",
        "QueryModel.Radius": "5000",
    }
    r = session.post(url, headers=headers, data=payload)
    website = "fultonbank.com"
    typ = "<MISSING>"
    country = "US"
    addlist = []
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "location-name" in line:
            items = line.split("location-name")
            for item in items:
                hours = ""
                if "location-address" in item:
                    name = (
                        item.split("\\u003e")[1]
                        .split("\\u003c")[0]
                        .replace("\\u0026amp;", "&")
                        .replace("\\u0026#39;", "'")
                    )
                    addinfo = (
                        item.split('on-address\\"\\u003e')[1]
                        .split("\\u003c/span")[0]
                        .replace("\\u0026#39;", "'")
                    )
                    addinfo = addinfo.replace("\\u0026amp;", "&")
                    add = addinfo.split(",")[0]
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                    zc = addinfo.rsplit(" ", 1)[1]
                    try:
                        lat = item.split('data-lat=\\"')[1].split("\\")[0]
                        lng = item.split('data-long=\\"')[1].split("\\")[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    try:
                        phone = item.split("Phone:")[1].split("\\")[0].strip()
                    except:
                        phone = "<MISSING>"
                    days = item.split('"hours-row\\"\\u003e')
                    dc = 0
                    for day in days:
                        if "location-address" not in day:
                            hrs = day.split("\\")[0]
                            dc = dc + 1
                            if dc <= 7:
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    addcity = add + "|" + city
                    if addcity not in addlist:
                        addlist.append(addcity)
                    if hours == "":
                        hours = "<MISSING>"
                    else:
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

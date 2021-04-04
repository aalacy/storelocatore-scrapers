import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("vince_com")


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
    url = "https://www.vince.com/on/demandware.store/Sites-vince-Site/default/Stores-GetNearestStores?latitude=40.7135097&longitude=-73.9859414&countryCode=US&distanceUnit=mi&maxdistance=10000"
    r = session.get(url, headers=headers)
    website = "vince.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"name":"' in line:
            items = line.split('"name":"')
            for item in items:
                CS = False
                if '"storeSecondaryName":"' in item:
                    if "Coming Soon" in item:
                        CS = True
                    loc = "<MISSING>"
                    store = "<MISSING>"
                    name = item.split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0]
                    add = add + " " + item.split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"stateCode":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    try:
                        hrs = item.split(',"storeHours":"')[1].split(
                            '","storeEvents":'
                        )[0]
                        hours = "Sun: " + hrs.split("Sunday")[1].split("<")[0]
                        hours = hours + "; Mon: " + hrs.split("Monday")[1].split("<")[0]
                        hours = (
                            hours + "; Tue: " + hrs.split("Tuesday")[1].split("<")[0]
                        )
                        hours = (
                            hours + "; Wed: " + hrs.split("Wednesday")[1].split("<")[0]
                        )
                        hours = (
                            hours + "; Thu: " + hrs.split("Thursday")[1].split("<")[0]
                        )
                        hours = hours + "; Fri: " + hrs.split("Friday")[1].split("<")[0]
                        hours = (
                            hours + "; Sat: " + hrs.split("Saturday")[1].split("<")[0]
                        )
                    except:
                        hours = "<MISSING>"
                    typ = item.split('"storeTypeDisplay":"')[1].split('"')[0]
                    if typ == "Retail" or typ == "Outlet":
                        if phone == "":
                            phone = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
                        add = add.replace("International Market Place", "").strip()
                        if "El Paseo Village" in add:
                            add = add.split("Paseo Village")[1].strip()
                        if "587 Newport" in add:
                            hours = "Sun: 12:00pm-6:00pm; Mon-Sat: 11:00am-7:00pm"
                        if "Draycott Avenue" not in add:
                            if CS is False:
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

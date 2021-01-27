import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer 90dd1fcea0074e7eb4b11e3753a0a334",
}

logger = SgLogSetup().get_logger("prohealthcare_com")


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
    infos = []
    urls = [
        "https://www.prohealthcare.com/bin/optumcare/findlocations?businessName=&fullName=&search=&latitude=40.75368539999999&longitude=-73.9991637&radius=100mi&network=ProHEALTHCare&isAcceptingNewPatients=true",
        "https://www.prohealthcare.com/bin/optumcare/findlocations?businessName=&fullName=&search=&latitude=42.75368539999999&longitude=-71.9991637&radius=100mi&network=ProHEALTHCare&isAcceptingNewPatients=true",
        "https://www.prohealthcare.com/bin/optumcare/findlocations?businessName=&fullName=&search=&latitude=38.75368539999999&longitude=-72.9991637&radius=100mi&network=ProHEALTHCare&isAcceptingNewPatients=true",
        "https://www.prohealthcare.com/bin/optumcare/findlocations?businessName=&fullName=&search=&latitude=40.75368539999999&longitude=-74.9991637&radius=100mi&network=ProHEALTHCare&isAcceptingNewPatients=true",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "prohealthcare.com"
        typ = "<MISSING>"
        country = "US"
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"individualProviderId":"' in line:
                items = line.split('"individualProviderId":"')
                for item in items:
                    if "providerRole" in item:
                        hours = ""
                        zc = item.split('"zip":"')[1].split('"')[0]
                        typ = item.split('{"specialty":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        lat = item.split('"lat_lon":"')[1].split('"')[0].split(",")[0]
                        lng = item.split('"lat_lon":"')[1].split('"')[0].split(",")[1]
                        add = item.split('"line1":"')[1].split('"')[0]
                        name = item.split('"businessName":"')[1].split('"')[0]
                        try:
                            phone = item.split('","telephoneUsage":"Office Phone"')[
                                0
                            ].rsplit('telephoneNumber":"', 1)[1]
                            phone = phone.replace("+1 ", "")
                        except:
                            phone = "<MISSING>"
                        days = item.split('"dayOfWeek":"')
                        for day in days:
                            if '"fromHour":"' in day:
                                hrs = (
                                    day.split('One"')[0]
                                    + ": "
                                    + day.split('"fromHour":"')[1].split('"')[0]
                                    + "-"
                                    + day.split('"toHour":"')[1].split('"')[0]
                                )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                        if hours == "":
                            hours = "<MISSING>"
                        addinfo = (
                            add
                            + "|"
                            + city
                            + "|"
                            + name
                            + "|"
                            + state
                            + "|"
                            + lat
                            + "|"
                            + phone
                        )
                        if addinfo not in infos:
                            infos.append(addinfo)
                            if "100-33 4th Ave" in add:
                                phone = "347-909-7044"
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

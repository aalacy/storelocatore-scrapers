import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("stateandmain_ca")


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
    url = "https://stateandmain.ca"
    r = session.get(url, headers=headers)
    website = "stateandmain.ca"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
            state = ""
            zc = ""
            loc = ""
            name = ""
            lat = ""
            lng = ""
            hours = ""
            phone = ""
            add = ""
            store = "<MISSING>"
        if '"postalCode": "' in line:
            zc = line.split('"postalCode": "')[1].split('"')[0]
        if '"province": "' in line:
            state = line.split('"province": "')[1].split('"')[0]
        if '"Title": "' in line:
            name = line.split('"Title": "')[1].split('"')[0]
        if '"slug": "' in line:
            loc = (
                "https://stateandmain.ca/home/"
                + line.split('"slug": "')[1].split('"')[0]
            )
        if '"geo": "' in line:
            lat = line.split('"geo": "')[1].split(",")[0]
            lng = line.split('"geo": "')[1].split(",")[1].split('"')[0]
        if '"telephone": "' in line:
            phone = line.split('"telephone": "')[1].split('"')[0]
        if '"streetAddress": "' in line:
            add = line.split('"streetAddress": "')[1].split('"')[0]
        if 'PM",' in line or 'OM",' in line or 'AM",' in line or 'Closed",' in line:
            hrs = line.split(",")[0].strip().replace("\t", "").replace('"', "")
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        if '"holidayHours": {' in line and city != "undefined":
            name = name.replace("&amp;", "&")
            hours = hours.replace("Temporarily : Closed", "Temporarily Closed").replace(
                "::", ":"
            )
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

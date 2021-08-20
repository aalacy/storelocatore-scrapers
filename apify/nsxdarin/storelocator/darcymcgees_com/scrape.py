import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("darcymcgees_com")


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
    locs = []
    url = "https://www.darcymcgees.com/en/locations.html"
    r = session.get(url, headers=headers)
    website = "darcymcgees.com"
    typ = "<MISSING>"
    ids = []
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'spreadsheetID: "' in line:
            sid = line.split(': "')[1].split('"')[0].replace("\\u002D", "-")
            locs.append(
                "https://spreadsheets.google.com/feeds/list/"
                + sid
                + "/1/public/values?alt=json"
            )
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"type":"text","$t":"storename:' in line2:
                items = line2.split('"type":"text","$t":"storename:')
                for item in items:
                    if "latitude:" in item:
                        lat = item.split("latitude:")[1].split(",")[0].strip()
                        lng = item.split("longitude:")[1].split(",")[0].strip()
                        add = item.split("streetnumber:")[1].split(",")[0].strip()
                        add = add + " " + item.split("street:")[1].split(",")[0].strip()
                        street = item.split("street:")[1].split(",")[0].strip()
                        city = item.split("city: ")[1].split(",")[0]
                        store = item.split('"gsx$storenumber":{"$t":"')[1].split('"')[0]
                        name = item.split('"gsx$storename":{"$t":"')[1].split('"')[0]
                        state = item.split("province: ")[1].split(",")[0]
                        zc = item.split("postalcode: ")[1].split(",")[0]
                        phone = item.split("phonenumber: ")[1].split(",")[0]
                        purl = (
                            "https://www.darcymcgees.com/en/locations/"
                            + store
                            + "/"
                            + city.lower().replace(".", "").replace("'", "")
                            + "-"
                            + street.replace(" ", "-").lower()
                            + ".html"
                        )
                        purl = purl
                        try:
                            hours = (
                                item.split("hours: ")[1]
                                .split(", emaila")[0]
                                .strip()
                                .replace("|", "")
                                .replace("\\n", "; ")
                                .replace("  ", " ")
                            )
                        except:
                            hours = "<MISSING>"
                        if "; , storenotice" in hours:
                            hours = hours.split("; , storenotice")[0].strip()
                        if ", storenotice" in hours:
                            hours = hours.split(", storenotice")[0].strip()
                        if "Holiday" in hours:
                            hours = hours.split("Holiday")[0].strip()
                        if store not in ids and "D'ARCY" in name.upper():
                            ids.append(store)
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

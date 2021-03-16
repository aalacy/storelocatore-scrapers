import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("amorino_com")


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
    url = "https://www.amorino.com/storelocator"
    r = session.get(url, headers=headers)
    website = "amorino.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ",stores:[{" in line:
            items = line.split("{country:au")
            for item in items:
                if ">window.__AMORINO__=" not in item:
                    name = item.split('name:"')[1].split('"')[0]
                    addinfo = item.split(',adress:"')[1].split('"')[0].strip()
                    addinfo = addinfo.replace("Street.", "Street,").replace(",,", ",")
                    addinfo = addinfo.replace("Orleans LA", "Orleans, LA")
                    addinfo = addinfo.replace("3393,", "3393")
                    addinfo = addinfo.replace("30326, Atlanta", "Atlanta, GA 30326")
                    addinfo = addinfo.replace("MA, 0", "MA 0")
                    addinfo = addinfo.replace("27601 NC", "NC 27601")
                    addinfo = addinfo.replace("G157, ", "G157 ").replace(
                        "Windrose Ave,", "Windrose Ave"
                    )
                    addinfo = addinfo.replace("338,", "338").replace("CA, 9", "CA 9")
                    addinfo = (
                        addinfo.replace("4444,", "4444")
                        .replace(", Unit", " Unit")
                        .replace("77027, Houston, TX", "Houston, TX 77027")
                    )
                    if "60 University Place" in addinfo:
                        add = "60 University Place"
                        city = "New York"
                        state = "NY"
                        zc = "<MISSING>"
                    elif "2965 Oakland" in addinfo:
                        add = "2965 Oakland Drive"
                        city = "Kalamazoo"
                        state = "MI"
                        zc = "49008"
                    elif "414, Amster" in addinfo:
                        add = "414 Amsterdam Avenue"
                        city = "New York"
                        state = "NY"
                        zc = "10024"
                    else:
                        add = addinfo.split(",")[0]
                        city = addinfo.split(",")[1].strip()
                        state = addinfo.split(",")[2].strip().split(" ")[0]
                        zc = addinfo.split(",")[2].rsplit(" ", 1)[1]
                    try:
                        phone = item.split(',phone:"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    lat = item.split("{lat:")[1].split(",")[0]
                    lng = item.split(",lng:")[1].split("}")[0]
                    loc = "<MISSING>"
                    try:
                        hours = (
                            item.split("weekday_text:[")[1]
                            .split("]")[0]
                            .replace('","', "; ")
                            .replace('"', "")
                        )
                    except:
                        hours = "<MISSING>"
                    hours = "<INACCESSIBLE>"
                    store = "<MISSING>"
                    if "637 Canal" in add:
                        phone = "504-510-2398"
                    if "7700 Windrose Ave" in add:
                        phone = "972-943-8534"
                    if "414 Amsterdam Avenue" in add:
                        phone = "212-877-5700"
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

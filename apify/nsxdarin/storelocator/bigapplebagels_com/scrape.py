import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bigapplebagels_com")


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
    coords = [
        "39.960535,-76.6807142",
        "42.6980038,-83.0942525",
        "44.7328441,-85.598073",
        "45.2734041,-92.9843644",
        "33.1359736,-117.1794402",
        "39.5955987,-104.8482404",
        "0,0",
        "28.1852784,-82.4214686",
    ]
    for coord in coords:
        url = (
            "https://bigapplebagels.com/Umbraco/Api/LocationsApi/GetNearbyLocations?latitude="
            + coord.split(",")[0]
            + "&longitude="
            + coord.split(",")[1]
            + "&maxResults=&maxDistance=5000"
        )
        r = session.get(url, headers=headers)
        website = "bigapplebagels.com"
        typ = "<MISSING>"
        country = "US"
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"Longitude":' in line:
                items = line.split('"Longitude":')
                for item in items:
                    if '"Latitude":' in item:
                        Closed = False
                        typ = "<MISSING>"
                        add = ""
                        lng = item.split(",")[0]
                        lat = item.split('"Latitude":')[1].split(",")[0]
                        name = item.split('"Name":"')[1].split('"')[0]
                        if "Temporarily Closed" in name:
                            Closed = True
                        try:
                            if (
                                "Temporarily Closed"
                                in item.split('"Address1":"')[1].split('"')[0]
                            ):
                                Closed = True
                        except:
                            pass
                        try:
                            add = item.split('"Address2":"')[1].split('"')[0]
                        except:
                            add = ""
                        if add == "":
                            try:
                                add = item.split('"Address1":"')[1].split('"')[0]
                            except:
                                pass
                        else:
                            try:
                                add = (
                                    add
                                    + " "
                                    + item.split('"Address1":"')[1].split('"')[0]
                                )
                            except:
                                pass
                        try:
                            city = item.split('"Locality":"')[1].split('"')[0]
                        except:
                            city = "<MISSING>"
                        try:
                            state = item.split('"Region":"')[1].split('"')[0]
                        except:
                            state = "<MISSING>"
                        try:
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                        except:
                            zc = "<MISSING>"
                        phone = item.split('"Phone":"')[1].split('"')[0]
                        store = item.split('"ID":')[1].split(",")[0]
                        hours = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        if lat == "0" or lat is None or lat == "0.0":
                            lat = "<MISSING>"
                        if lng == "0" or lng is None or lng == "0.0":
                            lng = "<MISSING>"
                        if add not in locs and add != "Test" and add != "":
                            locs.append(add)
                            if "*" in add:
                                add = add.split("*")[0].strip()
                            if "2616 Ogden" in add:
                                phone = "630-375-9822"
                            if Closed:
                                typ = "Temporarily Closed"
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

import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("conoco_com")

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
    ids = []
    for x in range(10, 65, 5):
        for y in range(-60, -170, -5):
            logger.info(str(x) + "," + str(y))
            url = (
                "https://spatial.virtualearth.net/REST/v1/data/a1ed23772f5f4994a096eaa782d07cfb/US_BrandedSites/Sites?spatialFilter=nearby("
                + str(x)
                + ","
                + str(y)
                + ",1000)&$filter=Confidence%20Eq%20%27High%27%20And%20(EntityType%20Eq%20%27Address%27%20Or%20EntityType%20Eq%20%27RoadIntersection%27)%20AND%20(Brand%20eq%20%27CON%27%20OR%20Brand%20Eq%20%27CON%27)&$format=json&$inlinecount=allpages&$select=*,__Distance&key=AqlID-ciQMxSAGsGXCatVwPLpgJOenb60MsckJMpLhyd0mxjEwEYN3ELSUCn2cQQ&$top=1000"
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode("utf-8"))
                if '"uri":"' in line:
                    items = line.split('"uri":"')
                    for item in items:
                        if '"EntityID":"' in item:
                            website = "conoco.com"
                            typ = item.split('"Brand":"')[1].split('"')[0]
                            store = item.split('"EntityID":"')[1].split('"')[0]
                            add = item.split('"AddressLine":"')[1].split('"')[0]
                            state = item.split('"AdminDistrict":"')[1].split('"')[0]
                            country = item.split('"CountryRegion":"')[1].split('"')[0]
                            city = item.split('"Locality":"')[1].split('"')[0]
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                            lat = item.split('"Latitude":')[1].split(",")[0]
                            lng = item.split('"Longitude":')[1].split(",")[0]
                            phone = item.split('"Phone":"')[1].split('"')[0]
                            name = (
                                item.split('"Name":"')[1]
                                .split('"')[0]
                                .replace("\\/", "/")
                            )
                            loc = (
                                "https://www.conoco.com/station/"
                                + typ
                                + "-"
                                + name.replace(" ", "-")
                                + "-"
                                + store
                            )
                            hours = "<MISSING>"
                            if phone == "":
                                phone = "<MISSING>"
                            mx = ["COA", "SIN", "SON", "CHI", "MX", "NL"]
                            if store not in ids and state not in mx:
                                if (
                                    "JUVENTINO" not in loc
                                    and "LAZARO" not in loc
                                    and "BENITO" not in loc
                                ):
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
                                    ids.append(store)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

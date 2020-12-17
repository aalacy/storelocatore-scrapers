import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("buybuybaby_com")


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
    url = "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh,2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22:%2264030%22,%22hostedDataList%22:[%7B%22extraCriteria%22:%22(+%5C%22display_online%5C%22+%3D+%3F+)+and+(+%5C%22store_type%5C%22+%3D+%3F+)%22,%22tableName%22:%22mqap.34703_AllInfo%22,%22parameters%22:[%22Y%22,%2240%22],%22columnNames%22:[]%7D],%22options%22:%7B%22radius%22:%223000%22,%22maxMatches%22:2000,%22ambiguities%22:%22ignore%22,%22units%22:%22m%22%7D%7D"
    r = session.get(url, headers=headers)
    website = "buybuybaby.com"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"distanceUnit":"' in line:
            items = line.split('{"distanceUnit":"')
            for item in items:
                if '"distance":' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    lng = item.split('"mqap_geography":{"latLng":{"lng":')[1].split(
                        ","
                    )[0]
                    lat = (
                        item.split('"mqap_geography":{"latLng":{"lng":')[1]
                        .split('"lat":')[1]
                        .split("}")[0]
                    )
                    hours = item.split('"hours":"')[1].split('"')[0]
                    store = item.split('"RecordId":"')[1].split('"')[0]
                    zc = item.split('"postal":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    phone = item.split('"Phone":"')[1].split('"')[0]
                    typ = "<MISSING>"
                    loc = "<MISSING>"
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

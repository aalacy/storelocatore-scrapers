import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("escada_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Winows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authority": "stockist.co",
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
    locs = []
    website = "escada.com"
    for x in range(10, 70, 10):
        for y in range(-170, -60, 10):
            xlat = str(x)
            ylng = str(y)
            logger.info(xlat + "," + ylng)
            url = (
                "https://stockist.co/api/v1/u6074/locations/search?tag=u6074&latitude="
                + xlat
                + "&longitude="
                + ylng
                + "&distance=10000"
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                line = str(line.decode("utf-8"))
                if '{"id":' in line:
                    items = line.split('{"id":')
                    for item in items:
                        if ',"name":"' in item:
                            name = item.split(',"name":"')[1].split('"')[0]
                            typ = "<MISSING>"
                            store = item.split(",")[0]
                            try:
                                lat = item.split(',"latitude":"')[1].split('"')[0]
                            except:
                                lat = "<MISSING>"
                            try:
                                lng = item.split('"longitude":"')[1].split('"')[0]
                            except:
                                lng = "<MISSING>"
                            try:
                                add = item.split('"address_line_1":"')[1].split('"')[0]
                            except:
                                add = "<MISSING>"
                            try:
                                city = item.split('"city":"')[1].split('"')[0]
                            except:
                                city = "<MISSING>"
                            try:
                                state = item.split('"state":"')[1].split('"')[0]
                            except:
                                state = "<MISSING>"
                            try:
                                country = item.split('"country":"')[1].split('"')[0]
                            except:
                                country = "<MISSING>"
                            if "Canada" in country:
                                country = "CA"
                            else:
                                country = "US"
                            try:
                                phone = item.split('"phone":"')[1].split('"')[0]
                            except:
                                phone = "<MISSING>"
                            try:
                                zc = item.split('"postal_code":"')[1].split('"')[0]
                            except:
                                zc = "<MISSING>"
                            hours = "<MISSING>"
                            lurl = "<MISSING>"
                            if "United States" in country:
                                country = "US"
                            if store not in locs:
                                if country == "CA" or country == "US":
                                    if (
                                        "-ku" not in add
                                        and "Mexico" not in city
                                        and "137." not in lng
                                        and "<MISSING>" not in add
                                    ):
                                        locs.append(store)
                                        yield [
                                            website,
                                            lurl,
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

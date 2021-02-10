import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("valero_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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
    url = "https://locations.valero.com/en-us/Home/SearchForLocations"
    coords = [
        "-60,-65",
        "-65,-70",
        "-70,-75",
        "-75,-80",
        "-80,-85",
        "-85,-90",
        "-90,-95",
        "-95,-100",
        "-100,-105",
        "-105,-110",
        "-110,-115",
        "-115,-120",
        "-120,-125",
        "-125,-130",
        "-130,-135",
        "-135,-140",
        "-140,-145",
        "-150,-155",
        "-160,-165",
        "-165,-170",
    ]

    latcoords = [
        "70,65",
        "65,60",
        "60,55",
        "55,50",
        "50,45",
        "45,40",
        "40,35",
        "35,30",
        "30,25",
        "25,20",
        "20,15",
        "15,10",
    ]

    for coord in coords:
        for latcoord in latcoords:
            logger.info(
                coord.split(",")[0]
                + "-"
                + coord.split(",")[1]
                + "; "
                + latcoord.split(",")[0]
                + ","
                + latcoord.split(",")[1]
            )
            payload = {
                "NEBound_Lat": latcoord.split(",")[0],
                "NEBound_Long": coord.split(",")[0],
                "SWBound_Lat": latcoord.split(",")[1],
                "SWBound_Long": coord.split(",")[1],
                "center_Lat": "",
                "center_Long": "",
            }

            r = session.post(url, headers=headers, data=payload)
            for line in r.iter_lines():
                line = str(line.decode("utf-8"))
                if '"Name":"' in line:
                    items = line.split('"Name":"')
                    for item in items:
                        if '"DirectionsURL":"' in item:
                            website = "valero.com"
                            country = "US"
                            zc = item.split('"PostalCode":"')[1].split('"')[0]
                            phone = item.split('"Phone":"')[1].split('"')[0]
                            lat = item.split('"Latitude":')[1].split(",")[0]
                            lng = item.split('"Longitude":')[1].split(",")[0]
                            typ = "<MISSING>"
                            name = (
                                item.split('"')[0]
                                .replace("\\u0026", "&")
                                .replace("\\u0027", "'")
                            )
                            store = item.split('"LocationDetails":[{"LocationID":"')[
                                1
                            ].split('"')[0]
                            purl = (
                                "https://locations.valero.com/en-us/LocationDetails/Index/"
                                + item.split('"DetailPageUrlID":"')[1].split('"')[0]
                                + "/"
                                + store
                            )
                            add = item.split('"AddressLine1":"')[1].split('"')[0]
                            try:
                                add = (
                                    add
                                    + " "
                                    + item.split('"AddressLine2":"')[1].split('"')[0]
                                )
                            except:
                                pass
                            city = item.split('"City":"')[1].split('"')[0]
                            state = item.split('"State":"')[1].split('"')[0]
                            hours = "<MISSING>"
                            if phone == "":
                                phone = "<MISSING>"
                            if phone == "0":
                                phone = "<MISSING>"
                            if (
                                "1" not in phone
                                and "2" not in phone
                                and "3" not in phone
                                and "4" not in phone
                                and "5" not in phone
                                and "6" not in phone
                                and "7" not in phone
                                and "8" not in phone
                                and "9" not in phone
                            ):
                                phone = "<MISSING>"
                            if store not in locs:
                                locs.append(store)
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

import csv
from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("kiehls_co_uk")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.BRITAIN],
    max_radius_miles=25,
    max_search_results=None,
)

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
    for lat, lng in search:
        try:
            x = lat
            y = lng
            url = (
                "https://www.kiehls.co.uk/on/demandware.store/Sites-kiehls-uk-v2-Site/en_GB/Stores-Search?unit=km&distance=25&lat="
                + str(x)
                + "&long="
                + str(y)
                + "&ajax=true"
            )
            logger.info("%s - %s..." % (str(x), str(y)))
            website = "kiehls.co.uk"
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)["storelocatorresults"]["stores"]:
                name = item["name"]
                logger.info(name)
                loc = "<MISSING>"
                add = item["address1"] + " " + item["address2"]
                add = add.strip().replace("\\n", ", ").replace("\n", ", ")
                if "," in add:
                    add = add.split(",")[0].strip()
                city = item["city"]
                if city == "":
                    city = "<MISSING>"
                phone = item["phone"]
                lat = item["latitude"]
                lng = item["longitude"]
                country = "GB"
                typ = "<MISSING>"
                store = item["id"]
                zc = item["postalCode"]
                hours = ""
                state = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                surl = "https://www.kiehls.co.uk/on/demandware.store/Sites-kiehls-uk-v2-Site/en_GB/Stores-Details?sid=" + store.replace(
                    "'", "%27"
                ).replace(
                    " ", "%20"
                )
                r2 = session.get(surl, headers=headers)
                alllines = ""
                for line2 in r2.iter_lines():
                    line2 = str(line2.decode("utf-8"))
                    alllines = alllines + line2.replace("\r", "").replace(
                        "\t", ""
                    ).replace("\n", "; ")
                try:
                    hours = alllines.split(
                        '<div class="c-storelocator__details-hours">'
                    )[1].split("<")[0]
                except:
                    hours = "<MISSING>"
                hours = hours.replace("/", "; ")
                if hours == "":
                    hours = "<MISSING>"
                if store == "":
                    store = "<MISSING>"
                if zc == "":
                    zc = "<MISSING>"
                hours = hours.replace("Tuesday", "; Tuesday")
                hours = hours.replace("Wednesday", "; Wednesday")
                hours = hours.replace("Thursday", "; Thursday")
                hours = hours.replace("Friday", "; Friday")
                hours = hours.replace("Saturday", "; Saturday")
                hours = (
                    hours.replace("day", "day ").replace(" ;", ";").replace("  ", " ")
                )
                if "Nk-Lisburn Road" in name:
                    add = "Unit 2 Osborne Buildings 717 Lisburn Road"
                if "Debenhams-Liverpool" in name:
                    add = "DEBENHAMS LIVERPOOL, UNIT 15 - 42 Lord Street"
                if "87-135 BROMPTON ROAD" in add:
                    add = "87-135 BROMPTON ROAD, Knightsbridge"
                if "Kiehl's-Windsor" in name:
                    add = "Unit 7, Windsor Royal Station Jubilee Arch"
                if "PADDINGTON STATION - The Lawn" in add:
                    add = "PADDINGTON STATION - The Lawn, Unit 3"
                if "Kiehl's-Waterloo" in name:
                    add = "UNIT 6, THE BALCONY - Waterloo Station"
                if "unit su-09" in add:
                    add = "unit su-09, Western arcade"
                if "307 Kings Road" in add:
                    add = "307 Kings Road (opposite Bluebird restaurant)"
                if "Westfield Whitecity" in name:
                    add = "Ariel Way, Shepherd's Bush"
                if "46 Northcote Road" in add:
                    add = "46 Northcote Road Clapham"
                if "Space Nk-Victoria" in name:
                    add = "Unit 6, 4 Cathedral Walk Cardinal Place"
                if "34 Hill Street" in add:
                    add = "34 Hill Street Richmond Surrey"
                if "Space Nk-Kingston" in name:
                    add = "2/2a Church Street Kingston-upon-Thames Surrey"
                if "INTU Watford" in add:
                    add = "INTU Watford, 300 the harlequin"
                if "29 Oakdene Parade" in add:
                    add = "29 Oakdene Parade Cobham Surrey"
                if "81 Queens Road" in add:
                    add = "81 Queens Road Clifton Bristol"
                if "Pedmore Rd" in add:
                    add = "Pedmore Rd, Brierley Hill"
                if "Unit 16-18" in add:
                    add = "Unit 16-18, Victoria Quarter Queen Victoria Quarter"
                if "2 The Highway" in add:
                    add = "2 The Highway Station Road"
                if "NO.38" in add:
                    add = "NO.38, HAYES ARCADE - St David's Dewi Sant"
                if "Space Nk-Windsor" in name:
                    add = "Unit 26, Windsor Royal Shopping Centre Windsor"
                if "Kiehl's-Nottingham" in name:
                    add = "14, ST PETERS GATE"
                if "36-37 Princes Square" in add:
                    add = "36-37 Princes Square 48 Buchanan Street"
                if "Space Nk-Bournemouth" in name:
                    add = "Unit 1, The Arcarde Gervis Place"
                if "Debenhams-Bournemouth" in name:
                    add = "The square, bourne Ave"
                if "Unit Ds1" in add:
                    add = "Unit Ds1, Overgate Centre"
                if "130 MERCHANT HALL" in add:
                    add = "130 MERCHANT HALL, CHAPELFIELD SHOPPING CENTRE"
                if (
                    ";Sunday" not in hours
                    and "; Sunday" not in hours
                    and "Sunday" in hours
                ):
                    hours = hours.replace("Sunday", "; Sunday")
                if add not in ids and city != "Online":
                    ids.append(add)
                    poi = [
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
                    yield poi
        except:
            pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

import csv
from sgrequests import SgRequests
import time
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("gasbuddy_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

states = [
    "AK",
    "AL",
    "AR",
    "AZ",
    "CA",
    "CO",
    "CT",
    "DC",
    "DE",
    "FL",
    "GA",
    "HI",
    "IA",
    "ID",
    "IL",
    "IN",
    "KS",
    "KY",
    "LA",
    "MA",
    "MD",
    "ME",
    "MI",
    "MN",
    "MO",
    "MS",
    "MT",
    "NC",
    "ND",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NV",
    "NY",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "UT",
    "VA",
    "VT",
    "WA",
    "WI",
    "WV",
    "WY",
]

provinces = ["AB", "BC", "MB", "NB", "NF", "NS", "NT", "QC", "PE", "QC", "SK"]

txcounties = [
    "2245:anderson",
    "767:andrews",
    "162:angelina",
    "2027:aransas",
    "2468:archer",
    "1526:armstrong",
    "207:atascosa",
    "451:austin",
    "867:bailey",
    "2036:bandera",
    "2282:bastrop",
    "3164:baylor",
    "1959:bee",
    "2280:bell",
    "2145:bexar",
    "37:blanco",
    "2706:bosque",
    "1557:bowie",
    "422:brazoria",
    "1162:brazos",
    "2046:brewster",
    "2315:briscoe",
    "1460:brooks",
    "59:brown",
    "1331:burleson",
    "2844:burnet",
    "1430:caldwell",
    "1981:calhoun",
    "79:callahan",
    "2999:cameron",
    "1945:camp",
    "2887:carson",
    "3194:cass",
    "3184:castro",
    "1107:chambers",
    "2034:cherokee",
    "2486:childress",
    "1493:clay",
    "2438:cochran",
    "1:coke",
    "1004:coleman",
    "2265:collin",
    "2243:collingsworth",
    "1181:colorado",
    "2417:comal",
    "2558:comanche",
    "2786:concho",
    "2454:cooke",
    "2453:coryell",
    "2388:cottle",
    "3149:crane",
    "1687:crockett",
    "496:crosby",
    "795:culberson",
    "2255:dallam",
    "499:dallas",
    "1294:dawson",
    "188:deaf-smith",
    "1613:delta",
    "583:denton",
    "3053:dewitt",
    "2471:dickens",
    "1486:dimmit",
    "3193:donley",
    "1982:duval",
    "2801:eastland",
    "2124:ector",
    "2898:edwards",
    "3136:ellis",
    "406:el-paso",
    "266:erath",
    "1684:falls",
    "151:fannin",
    "3034:fayette",
    "2606:fisher",
    "1809:floyd",
    "2404:foard",
    "1454:fort-bend",
    "1114:franklin",
    "518:freestone",
    "2148:frio",
    "2561:gaines",
    "2175:galveston",
    "2547:garza",
    "450:gillespie",
    "2712:glasscock",
    "2952:goliad",
    "2926:gonzales",
    "347:gray",
    "1126:grayson",
    "2719:gregg",
    "2067:grimes",
    "2862:guadalupe",
    "1381:hale",
    "2316:hall",
    "2727:hamilton",
    "2580:hansford",
    "220:hardeman",
    "1261:hardin",
    "3094:harris",
    "2480:harrison",
    "2082:hartley",
    "995:haskell",
    "613:hays",
    "1:hemphill",
    "1077:henderson",
    "2892:hidalgo",
    "641:hill",
    "2476:hockley",
    "3119:hood",
    "3219:hopkins",
    "2785:houston",
    "2666:howard",
    "2731:hudspeth",
    "3025:hunt",
    "287:hutchinson",
    "2788:irion",
    "2528:jack",
    "1191:jackson",
    "3058:jasper",
    "3124:jeff-davis",
    "2510:jefferson",
    "1306:jim-hogg",
    "2974:jim-wells",
    "283:johnson",
    "2786:jones",
    "560:karnes",
    "304:kaufman",
    "2978:kendall",
    "2540:kent",
    "2897:kerr",
    "2830:kimble",
    "2933:kinney",
    "712:kleberg",
    "2470:knox",
    "2820:lamar",
    "2292:lamb",
    "72:lampasas",
    "2126:la-salle",
    "2634:lavaca",
    "2311:lee",
    "989:leon",
    "225:liberty",
    "1208:limestone",
    "1992:lipscomb",
    "1338:live-oak",
    "2856:llano",
    "57:lubbock",
    "2075:lynn",
    "2966:madison",
    "2315:marion",
    "1087:martin",
    "2855:mason",
    "1224:matagorda",
    "137:maverick",
    "1468:mcculloch",
    "356:mclennan",
    "2962:mcmullen",
    "754:medina",
    "2834:menard",
    "2370:midland",
    "2521:milam",
    "1745:mills",
    "2745:mitchell",
    "2195:montague",
    "2877:montgomery",
    "2081:moore",
    "1071:morris",
    "2387:motley",
    "2128:nacogdoches",
    "2644:navarro",
    "49:newton",
    "742:nolan",
    "1850:nueces",
    "984:ochiltree",
    "2159:oldham",
    "2765:orange",
    "395:palo-pinto",
    "2704:panola",
    "655:parker",
    "2319:parmer",
    "1693:pecos",
    "1994:polk",
    "1418:potter",
    "1787:presidio",
    "297:rains",
    "1690:randall",
    "1920:reagan",
    "2913:real",
    "2451:red-river",
    "2908:reeves",
    "1543:refugio",
    "2078:roberts",
    "2811:robertson",
    "689:rockwall",
    "487:runnels",
    "58:rusk",
    "2782:sabine",
    "3065:san-augustine",
    "545:san-jacinto",
    "2064:san-patricio",
    "2794:san-saba",
    "2833:schleicher",
    "1763:scurry",
    "2611:shackelford",
    "50:shelby",
    "1991:sherman",
    "1109:smith",
    "941:somervell",
    "1662:starr",
    "3151:stephens",
    "2713:sterling",
    "2544:stonewall",
    "1638:sutton",
    "1482:swisher",
    "2576:tarrant",
    "2668:taylor",
    "2873:terrell",
    "2930:terry",
    "2542:throckmorton",
    "1399:titus",
    "2769:tom-green",
    "2879:travis",
    "2093:trinity",
    "2624:tyler",
    "3203:upshur",
    "154:upton",
    "2039:uvalde",
    "1326:val-verde",
    "1005:van-zandt",
    "113:victoria",
    "2802:walker",
    "955:waller",
    "1226:ward",
    "1580:washington",
    "1728:webb",
    "264:wharton",
    "2163:wheeler",
    "600:wichita",
    "1553:wilbarger",
    "1780:willacy",
    "1537:williamson",
    "938:wilson",
    "2172:winkler",
    "2972:wise",
]


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "open_status",
                "status",
                "branding_type",
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
    locinfo = []
    website = "gasbuddy.com"
    for state in states:
        count = 0
        Found = True
        while Found:
            Found = False
            time.sleep(1)
            logger.info(state + ": " + str(count))
            url = (
                "https://www.gasbuddy.com/assets-v2/api/stations?regionCode="
                + state.strip()
                + "&fuel=1&maxAge=0&cursor="
                + str(count)
                + "&countryCode=US"
            )
            r = session.get(url, headers=headers)
            count = count + 25
            try:
                for item in json.loads(r.content)["stations"]:
                    Found = True
                    store = item["id"]
                    country = item["address"]["country"]
                    name = item["name"]
                    typ = item["item_type"]
                    typ = str(typ).replace("[", "").replace("]", "").replace("'", "")
                    add = item["address"]["line_1"] + " " + item["address"]["line_2"]
                    add = add.strip()
                    city = item["address"]["locality"]
                    state = item["address"]["region"]
                    zc = item["address"]["postal_code"]
                    phone = item["phone"]
                    try:
                        hours = item["opening_hours"]
                    except:
                        hours = "<MISSING>"
                    lat = item["latitude"]
                    lng = item["longitude"]
                    loc = "<MISSING>"
                    if phone == "" or phone is None:
                        phone = "<MISSING>"
                    if zc == "":
                        zc = "<MISSING>"
                    os = item["open_status"]
                    stat = item["status"]
                    if state == "":
                        state = "<MISSING>"
                    add = add.replace('"', "'")
                    btype = ""
                    try:
                        for brand in item["brandings"]:
                            if btype == "":
                                btype = brand["branding_type"]
                            else:
                                btype = btype + ", " + brand["branding_type"]
                    except:
                        btype = "<MISSING>"
                    addinfo = add + "|" + city + "|" + state + "|" + zc
                    if addinfo not in locinfo:
                        locinfo.append(addinfo)
                        yield [
                            website,
                            loc,
                            os,
                            stat,
                            btype,
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
            except:
                Found = False

    website = "gasbuddy.com"
    for county in txcounties:
        count = 0
        cname = county.split(":")[1]
        cid = county.split(":")[0]
        Found = True
        while Found:
            Found = False
            time.sleep(1)
            logger.info(county + ": " + str(count))
            url = (
                "https://www.gasbuddy.com/assets-v2/api/stations?area="
                + cname.strip()
                + "&countyId="
                + cid.strip()
                + "&cursor="
                + str(count)
                + "&regionCode=TX&countryCode=US"
            )
            r = session.get(url, headers=headers)
            count = count + 25
            try:
                for item in json.loads(r.content)["stations"]:
                    Found = True
                    store = item["id"]
                    country = item["address"]["country"]
                    name = item["name"]
                    typ = item["item_type"]
                    typ = str(typ).replace("[", "").replace("]", "").replace("'", "")
                    add = item["address"]["line_1"] + " " + item["address"]["line_2"]
                    add = add.strip()
                    city = item["address"]["locality"]
                    state = item["address"]["region"]
                    zc = item["address"]["postal_code"]
                    phone = item["phone"]
                    try:
                        hours = item["opening_hours"]
                    except:
                        hours = "<MISSING>"
                    lat = item["latitude"]
                    lng = item["longitude"]
                    loc = "<MISSING>"
                    if phone == "" or phone is None:
                        phone = "<MISSING>"
                    if zc == "":
                        zc = "<MISSING>"
                    os = item["open_status"]
                    stat = item["status"]
                    if state == "":
                        state = "<MISSING>"
                    add = add.replace('"', "'")
                    btype = ""
                    try:
                        for brand in item["brandings"]:
                            if btype == "":
                                btype = brand["branding_type"]
                            else:
                                btype = btype + ", " + brand["branding_type"]
                    except:
                        btype = "<MISSING>"
                    addinfo = add + "|" + city + "|" + state + "|" + zc
                    if addinfo not in locinfo:
                        locinfo.append(addinfo)
                        yield [
                            website,
                            loc,
                            os,
                            stat,
                            btype,
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
            except:
                Found = False

    website = "gasbuddy.com"
    for state in provinces:
        count = 0
        Found = True
        while Found:
            Found = False
            time.sleep(1)
            logger.info(state + ": " + str(count))
            url = (
                "https://www.gasbuddy.com/assets-v2/api/stations?regionCode="
                + state.strip()
                + "&fuel=1&maxAge=0&cursor="
                + str(count)
                + "&countryCode=CA"
            )
            r = session.get(url, headers=headers)
            count = count + 25
            try:
                for item in json.loads(r.content)["stations"]:
                    Found = True
                    store = item["id"]
                    country = item["address"]["country"]
                    name = item["name"]
                    typ = item["item_type"]
                    typ = str(typ).replace("[", "").replace("]", "").replace("'", "")
                    add = item["address"]["line_1"] + " " + item["address"]["line_2"]
                    add = add.strip()
                    city = item["address"]["locality"]
                    state = item["address"]["region"]
                    zc = item["address"]["postal_code"]
                    phone = item["phone"]
                    try:
                        hours = item["opening_hours"]
                    except:
                        hours = "<MISSING>"
                    lat = item["latitude"]
                    lng = item["longitude"]
                    loc = "<MISSING>"
                    if phone == "" or phone is None:
                        phone = "<MISSING>"
                    if zc == "":
                        zc = "<MISSING>"
                    os = item["open_status"]
                    stat = item["status"]
                    if state == "":
                        state = "<MISSING>"
                    add = add.replace('"', "'")
                    btype = ""
                    try:
                        for brand in item["brandings"]:
                            if btype == "":
                                btype = brand["branding_type"]
                            else:
                                btype = btype + ", " + brand["branding_type"]
                    except:
                        btype = "<MISSING>"
                    addinfo = add + "|" + city + "|" + state + "|" + zc
                    if addinfo not in locinfo:
                        locinfo.append(addinfo)
                        yield [
                            website,
                            loc,
                            os,
                            stat,
                            btype,
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
            except:
                Found = False


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

import csv
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("ford_ca")


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


@retry(stop=stop_after_attempt(10))
def api_call(url):
    session = SgRequests()
    return session.get(url, headers=headers, timeout=10).json()


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
    canada = [
        "Toronto,ON",
        "Montreal,QC",
        "Calgary,AB",
        "Ottawa,ON",
        "Edmonton,AB",
        "Mississauga,ON",
        "Winnipeg,MB",
        "Vancouver,BC",
        "Brampton,ON",
        "Hamilton,ON",
        "Quebec,QC",
        "Surrey,BC",
        "Laval,QC",
        "Halifax,NS",
        "London,ON",
        "Markham,ON",
        "Vaughan,ON",
        "Gatineau,QC",
        "Saskatoon,SK",
        "Longueuil,QC",
        "Kitchener,ON",
        "Burnaby,BC",
        "Windsor,ON",
        "Regina,SK",
        "Richmond,BC",
        "Richmond Hill,ON",
        "Oakville,ON",
        "Burlington,ON",
        "Greater Sudbury,ON",
        "Sherbrooke,QC",
        "Oshawa,ON",
        "Saguenay,QC",
        "Levis,QC",
        "Barrie,ON",
        "Abbotsford,BC",
        "Coquitlam,BC",
        "Trois Rivieres,QC",
        "St Catharines,ON",
        "Guelph,ON",
        "Cambridge,ON",
        "Whitby,ON",
        "Kelowna,BC",
        "Kingston,ON",
        "Ajax,ON",
        "Langley District Municipality,BC",
        "Saanich,BC",
        "Terrebonne,QC",
        "Milton,ON",
        "St Johns,NL",
        "Thunder Bay,ON",
        "Waterloo,ON",
        "Delta,BC",
        "Chatham Kent,ON",
        "Red Deer,AB",
        "Strathcona County,AB",
        "Brantford,ON",
        "St Jean sur Richelieu,QC",
        "Cape Breton,NS",
        "Lethbridge,AB",
        "Clarington,ON",
        "Pickering,ON",
        "Nanaimo,BC",
        "Kamloops,BC",
        "Niagara Falls,ON",
        "North Vancouver District Municipality,BC",
        "Victoria,BC",
        "Brossard,QC",
        "Repentigny,QC",
        "Newmarket,ON",
        "Chilliwack,BC",
        "Maple Ridge,BC",
        "Peterborough,ON",
        "Kawartha Lakes,ON",
        "Drummondville,QC",
        "St Jerome,QC",
        "Prince George,BC",
        "Sault Ste Marie,ON",
        "Moncton,NB",
        "Sarnia,ON",
        "Wood Buffalo,AB",
        "New Westminster,BC",
        "St John,NB",
        "Caledon,ON",
        "Granby,QC",
        "St Albert,AB",
        "Norfolk County,ON",
        "Medicine Hat,AB",
        "Grande Prairie,AB",
        "Airdrie,AB",
        "Halton Hills,ON",
        "Port Coquitlam,BC",
        "Fredericton,NB",
        "Blainville,QC",
        "St Hyacinthe,QC",
        "Aurora,ON",
        "North Vancouver,BC",
        "Welland,ON",
        "North Bay,ON",
        "Belleville,ON",
        "Mirabel,QC",
        "Shawinigan,QC",
        "Dollard Des Ormeaux,QC",
        "Brandon,MB",
        "Rimouski,QC",
        "Chateauguay,QC",
        "Mascouche,QC",
        "Cornwall,ON",
        "Victoriaville,QC",
        "Whitchurch Stouffville,ON",
        "Haldimand County,ON",
        "Georgina,ON",
        "St Eustache,QC",
        "Quinte West,ON",
        "West Vancouver,BC",
        "Rouyn Noranda,QC",
        "Timmins,ON",
        "Boucherville,QC",
        "Woodstock,ON",
        "Salaberry de Valleyfield,QC",
        "Vernon,BC",
        "St Thomas,ON",
        "Mission,BC",
        "Vaudreuil Dorion,QC",
        "Brant,ON",
        "Lakeshore,ON",
        "Innisfil,ON",
        "Charlottetown,PE",
        "Prince Albert,SK",
        "Langford,BC",
        "Bradford West Gwillimbury,ON",
        "Sorel Tracy,QC",
        "New Tecumseth,ON",
        "Spruce Grove,AB",
        "Moose Jaw,SK",
        "Penticton,BC",
        "Port Moody,BC",
        "West Kelowna,BC",
        "Campbell River,BC",
        "St Georges,QC",
        "Val dOr,QC",
        "Cote St Luc,QC",
        "Stratford,ON",
        "Pointe Claire,QC",
        "Orillia,ON",
        "Alma,QC",
        "Fort Erie,ON",
        "LaSalle,ON",
        "Leduc,AB",
        "Ste Julie,QC",
        "North Cowichan,BC",
        "Chambly,QC",
        "Orangeville,ON",
        "Okotoks,AB",
        "Leamington,ON",
        "St Constant,QC",
        "Grimsby,ON",
        "Boisbriand,QC",
        "Magog,QC",
        "St Bruno de Montarville,QC",
        "Conception Bay South,NL",
        "Ste Therese,QC",
        "Langley,BC",
        "Cochrane,AB",
        "Courtenay,BC",
        "Thetford Mines,QC",
        "Sept Iles,QC",
        "Dieppe,NB",
        "Whitehorse,YT",
        "Prince Edward County,ON",
        "Clarence Rockland,ON",
        "Fort Saskatchewan,AB",
        "La Prairie,QC",
        "East Gwillimbury,ON",
        "Lincoln,ON",
        "Tecumseh,ON",
        "Mount Pearl,NL",
        "Beloeil,QC",
        "LAssomption,QC",
        "Amherstburg,ON",
        "St Lambert,QC",
        "Collingwood,ON",
        "Kingsville,ON",
        "Baie Comeau,QC",
        "Paradise,NL",
        "Brockville,ON",
        "Owen Sound,ON",
        "Varennes,QC",
        "Candiac,QC",
        "Strathroy Caradoc,ON",
        "St Lin Laurentides,QC",
        "Wasaga Beach,ON",
        "Joliette,QC",
        "Essex,ON",
        "Westmount,QC",
        "Mont Royal,QC",
        "Fort St John,BC",
        "Kirkland,QC",
        "Cranbrook,BC",
        "White Rock,BC",
        "St Lazare,QC",
    ]
    for loc in canada:
        logger.info("Pulling City %s..." % loc)
        ccity = loc.split(",")[0].strip()
        cprov = loc.split(",")[1].strip()
        url = (
            "https://www.ford.ca/services/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&city="
            + ccity
            + "&province="
            + cprov
            + "&api_key=3b0d0b6c-56fb-a02c-a0d03a98-2e06d595"
        )
        js = api_call(url)
        if "Dealer" in js["Response"]:
            dealers = (
                js["Response"]["Dealer"]
                if isinstance(js["Response"]["Dealer"], list)
                else [js["Response"]["Dealer"]]
            )
            for item in dealers:
                lng = item["Longitude"]
                lat = item["Latitude"]
                name = item["Name"]
                typ = item["dealerType"]
                website = "ford.ca"
                purl = item["URL"]
                hours = ""
                add = (
                    item["Address"]["Street1"]
                    + " "
                    + item["Address"]["Street2"]
                    + " "
                    + item["Address"]["Street3"]
                )
                add = add.strip()
                city = item["Address"]["City"]
                state = item["Address"]["Province"]
                country = item["Address"]["Country"][:2]
                zc = item["Address"]["PostalCode"]
                store = item["SalesCode"]
                phone = item["Phone"]
                daytext = str(item["SalesHours"])
                daytext = daytext.replace("'", '"')
                daytext = daytext.replace('u"', '"').replace(" {", "{")
                days = daytext.split(",{")
                for day in days:
                    if '"name": "' in day:
                        dname = day.split('"name": "')[1].split('"')[0]
                        if '"closed": "true"' in day:
                            hrs = "Closed"
                        else:
                            hrs = (
                                day.split('"open": "')[1].split('"')[0]
                                + "-"
                                + day.split('"close": "')[1].split('"')[0]
                            )
                        if hours == "":
                            hours = dname + ": " + hrs
                        else:
                            hours = hours + "; " + dname + ": " + hrs
                try:
                    purl = item["URL"]
                except:
                    purl = "<MISSING>"
                if store not in ids:
                    ids.append(store)
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if purl == "" or purl is None:
                        purl = "<MISSING>"
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

import csv
from sgrequests import SgRequests
import sgzip
import time
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("bobcat_com")

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
    for code in sgzip.for_radius(100):
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://bobcat.know-where.com/bobcat/cgi/selection?place="
            + code
            + "&lang=en&option=&ll=&stype=place&async=results"
        )
        session = SgRequests()
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        time.sleep(3)
        lat = "<MISSING>"
        lng = "<MISSING>"
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            website = "bobcat.com"
            if '<h4 style="margin: 0; color: black; font-size: 18px">' in line:
                name = line.split(
                    '<h4 style="margin: 0; color: black; font-size: 18px">'
                )[1].split("<")[0]
                typ = "Dealer"
            if "onclick=\"KW.bobcat.toggleDetail('" in line:
                store = line.split("onclick=\"KW.bobcat.toggleDetail('")[1].split("'")[
                    0
                ]
            if '<span onclick="">' in line:
                raw_address = (
                    next(lines)
                    .split("<div>")[1]
                    .split("</div>")[0]
                    .replace("Ave", "Avenue")
                    .replace("Avenuenue", "Avenue")
                )
                tel_line = next(lines)
                while "tel:" not in tel_line:
                    tel_line = next(lines)
                phone = tel_line.split("tel:1")[1].split('"')[0].replace("'", "")
                if 'website-icon.png"' in tel_line:
                    purl = (
                        tel_line.split('website-icon.png">')[1]
                        .split("this.href='")[1]
                        .split("'")[0]
                    )
                else:
                    purl = "<MISSING>"
                try:
                    tagged = usaddress.tag(raw_address)[0]
                    city = tagged.get("PlaceName", "<MISSING>")
                    state = tagged.get("StateName", "<MISSING>")
                    zc = tagged.get("ZipCode", "<MISSING>")
                    if city != "<MISSING>":
                        add = raw_address.split(city)[0].strip()
                    else:
                        add = raw_address.split(",")[0]
                except:
                    zc = raw_address.strip().rsplit(" ")[1]
                    state = raw_address.strip().split(" ")[-2]
                    city = raw_address.strip().split(",")[0].split(" ")[1]
                    add = raw_address.strip().split(",")[0].split(" ")[0]
                country = "US"
                hours = "<MISSING>"
                if store not in ids:
                    ids.append(store)
                    name = name.replace('"', "'")
                    add = add.replace('"', "'")
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

    cities = [
        "Toronto%2C%20ON",
        "Montreal%2C%20QB",
        "Calgary%2C%20AB",
        "Ottawa%2C%20ON",
        "Edmonton%2C%20AB",
        "Mississauga%2C%20ON",
        "Winnipeg%2C%20MB",
        "Vancouver%2C%20BC",
        "Brampton%2C%20ON",
        "Hamilton%2C%20ON",
        "Quebec%2C%20QB",
        "Surrey%2C%20BC",
        "Laval%2C%20QB",
        "Halifax%2C%20NS",
        "London%2C%20ON",
        "Markham%2C%20ON",
        "Vaughan%2C%20ON",
        "Gatineau%2C%20QB",
        "Saskatoon%2C%20SK",
        "Longueuil%2C%20QB",
        "Kitchener%2C%20ON",
        "Burnaby%2C%20BC",
        "Windsor%2C%20ON",
        "Regina%2C%20SK",
        "Richmond%2C%20BC",
        "Richmond%20Hill%2C%20ON",
        "Oakville%2C%20ON",
        "Burlington%2C%20ON",
        "Greater%20Sudbury%2C%20ON",
        "Sherbrooke%2C%20QB",
        "Oshawa%2C%20ON",
        "Saguenay%2C%20QB",
        "Levis%2C%20QB",
        "Barrie%2C%20ON",
        "Abbotsford%2C%20BC",
        "Coquitlam%2C%20BC",
        "Trois%20Rivieres%2C%20QB",
        "St%20Catharines%2C%20ON",
        "Guelph%2C%20ON",
        "Cambridge%2C%20ON",
        "Whitby%2C%20ON",
        "Kelowna%2C%20BC",
        "Kingston%2C%20ON",
        "Ajax%2C%20ON",
        "Langley%20District%20Municipality%2C%20BC",
        "Saanich%2C%20BC",
        "Terrebonne%2C%20QB",
        "Milton%2C%20ON",
        "St%20Johns%2C%20NL",
        "Thunder%20Bay%2C%20ON",
        "Waterloo%2C%20ON",
        "Delta%2C%20BC",
        "Chatham%20Kent%2C%20ON",
        "Red%20Deer%2C%20AB",
        "Strathcona%20County%2C%20AB",
        "Brantford%2C%20ON",
        "St%20Jean%20sur%20Richelieu%2C%20QB",
        "Cape%20Breton%2C%20NS",
        "Lethbridge%2C%20AB",
        "Clarington%2C%20ON",
        "Pickering%2C%20ON",
        "Nanaimo%2C%20BC",
        "Kamloops%2C%20BC",
        "Niagara%20Falls%2C%20ON",
        "North%20Vancouver%20District%20Municipality%2C%20BC",
        "Victoria%2C%20BC",
        "Brossard%2C%20QB",
        "Repentigny%2C%20QB",
        "Newmarket%2C%20ON",
        "Chilliwack%2C%20BC",
        "Maple%20Ridge%2C%20BC",
        "Peterborough%2C%20ON",
        "Kawartha%20Lakes%2C%20ON",
        "Drummondville%2C%20QB",
        "St%20Jerome%2C%20QB",
        "Prince%20George%2C%20BC",
        "Sault%20Ste%20Marie%2C%20ON",
        "Moncton%2C%20NB",
        "Sarnia%2C%20ON",
        "Wood%20Buffalo%2C%20AB",
        "New%20Westminster%2C%20BC",
        "St%20John%2C%20NB",
        "Caledon%2C%20ON",
        "Granby%2C%20QB",
        "St%20Albert%2C%20AB",
        "Norfolk%20County%2C%20ON",
        "Medicine%20Hat%2C%20AB",
        "Grande%20Prairie%2C%20AB",
        "Airdrie%2C%20AB",
        "Halton%20Hills%2C%20ON",
        "Port%20Coquitlam%2C%20BC",
        "Fredericton%2C%20NB",
        "Blainville%2C%20QB",
        "St%20Hyacinthe%2C%20QB",
        "Aurora%2C%20ON",
        "North%20Vancouver%2C%20BC",
        "Welland%2C%20ON",
        "North%20Bay%2C%20ON",
        "Belleville%2C%20ON",
        "Mirabel%2C%20QB",
        "Shawinigan%2C%20QB",
        "Dollard%20Des%20Ormeaux%2C%20QB",
        "Brandon%2C%20MB",
        "Rimouski%2C%20QB",
        "Chateauguay%2C%20QB",
        "Mascouche%2C%20QB",
        "Cornwall%2C%20ON",
        "Victoriaville%2C%20QB",
        "Whitchurch%20Stouffville%2C%20ON",
        "Haldimand%20County%2C%20ON",
        "Georgina%2C%20ON",
        "St%20Eustache%2C%20QB",
        "Quinte%20West%2C%20ON",
        "West%20Vancouver%2C%20BC",
        "Rouyn%20Noranda%2C%20QB",
        "Timmins%2C%20ON",
        "Boucherville%2C%20QB",
        "Woodstock%2C%20ON",
        "Salaberry%20de%20Valleyfield%2C%20QB",
        "Vernon%2C%20BC",
        "St%20Thomas%2C%20ON",
        "Mission%2C%20BC",
        "Vaudreuil%20Dorion%2C%20QB",
        "Brant%2C%20ON",
        "Lakeshore%2C%20ON",
        "Innisfil%2C%20ON",
        "Charlottetown%2C%20PE",
        "Prince%20Albert%2C%20SK",
        "Langford%2C%20BC",
        "Bradford%20West%20Gwillimbury%2C%20ON",
        "Sorel%20Tracy%2C%20QB",
        "New%20Tecumseth%2C%20ON",
        "Spruce%20Grove%2C%20AB",
        "Moose%20Jaw%2C%20SK",
        "Penticton%2C%20BC",
        "Port%20Moody%2C%20BC",
        "West%20Kelowna%2C%20BC",
        "Campbell%20River%2C%20BC",
        "St%20Georges%2C%20QB",
        "Val%20dOr%2C%20QB",
        "Cote%20St%20Luc%2C%20QB",
        "Stratford%2C%20ON",
        "Pointe%20Claire%2C%20QB",
        "Orillia%2C%20ON",
        "Alma%2C%20QB",
        "Fort%20Erie%2C%20ON",
        "LaSalle%2C%20ON",
        "Leduc%2C%20AB",
        "Ste%20Julie%2C%20QB",
        "North%20Cowichan%2C%20BC",
        "Chambly%2C%20QB",
        "Orangeville%2C%20ON",
        "Okotoks%2C%20AB",
        "Leamington%2C%20ON",
        "St%20Constant%2C%20QB",
        "Grimsby%2C%20ON",
        "Boisbriand%2C%20QB",
        "Magog%2C%20QB",
        "St%20Bruno%20de%20Montarville%2C%20QB",
        "Conception%20Bay%20South%2C%20NL",
        "Ste%20Therese%2C%20QB",
        "Langley%2C%20BC",
        "Cochrane%2C%20AB",
        "Courtenay%2C%20BC",
        "Thetford%20Mines%2C%20QB",
        "Sept%20Iles%2C%20QB",
        "Dieppe%2C%20NB",
        "Whitehorse%2C%20YT",
        "Prince%20Edward%20County%2C%20ON",
        "Clarence%20Rockland%2C%20ON",
        "Fort%20Saskatchewan%2C%20AB",
        "La%20Prairie%2C%20QB",
        "East%20Gwillimbury%2C%20ON",
        "Lincoln%2C%20ON",
        "Tecumseh%2C%20ON",
        "Mount%20Pearl%2C%20NL",
        "Beloeil%2C%20QB",
        "LAssomption%2C%20QB",
        "Amherstburg%2C%20ON",
        "St%20Lambert%2C%20QB",
        "Collingwood%2C%20ON",
        "Kingsville%2C%20ON",
        "Baie%20Comeau%2C%20QB",
        "Paradise%2C%20NL",
        "Brockville%2C%20ON",
        "Owen%20Sound%2C%20ON",
        "Varennes%2C%20QB",
        "Candiac%2C%20QB",
        "Strathroy%20Caradoc%2C%20ON",
        "St%20Lin%20Laurentides%2C%20QB",
        "Wasaga%20Beach%2C%20ON",
        "Joliette%2C%20QB",
        "Essex%2C%20ON",
        "Westmount%2C%20QB",
        "Mont%20Royal%2C%20QB",
        "Fort%20St%20John%2C%20BC",
        "Kirkland%2C%20QB",
        "Cranbrook%2C%20BC",
        "White%20Rock%2C%20BC",
        "St%20Lazare%2C%20QB",
    ]

    for city in cities:
        logger.info(("Pulling CA City %s..." % city))
        url = (
            "https://bobcat.know-where.com/bobcat/cgi/selection?place="
            + city
            + "&lang=en&ll=&stype=place&async=results"
        )
        r = session.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        time.sleep(3)
        lat = "<MISSING>"
        lng = "<MISSING>"
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            website = "bobcat.com"
            if '<h4 style="margin: 0; color: black; font-size: 18px">' in line:
                name = line.split(
                    '<h4 style="margin: 0; color: black; font-size: 18px">'
                )[1].split("<")[0]
                typ = "Dealer"
            if '<span onclick="">' in line:
                store = line.split("toggleDetail('")[1].split("'")[0]
                raw_address = next(lines).split("<div>")[1].split("</div>")[0]
                tel_line = next(lines)
                while "tel:" not in tel_line:
                    tel_line = next(lines)
                phone = tel_line.split("tel:1")[1].split('"')[0]
                if 'website-icon.png"' in tel_line:
                    purl = (
                        tel_line.split('website-icon.png">')[1]
                        .split("this.href='")[1]
                        .split("'")[0]
                    )
                else:
                    purl = "<MISSING>"
                try:
                    tagged = usaddress.tag(raw_address)[0]
                    city = tagged.get("PlaceName", "<MISSING>")
                    state = tagged.get("StateName", "<MISSING>")
                    zc = tagged.get("ZipCode", "<MISSING>")
                    if city != "<MISSING>":
                        add = raw_address.split(city)[0].strip()
                    else:
                        add = raw_address.split(",")[0]
                except:
                    zc = raw_address.strip().rsplit(" ", 2)[1]
                    state = raw_address.strip().split(" ")[-2]
                    city = raw_address.strip().split(",")[0].split(" ")[1]
                    add = raw_address.strip().split(",")[0].split(" ")[0]
                country = "CA"
                hours = "<MISSING>"
                if zc != "<MISSING>":
                    try:
                        zc = state.split(" ")[1] + " " + zc
                        state = state.split(" ")[0]
                    except:
                        zc = "<MISSING>"
                else:
                    if " " in state:
                        state = state.split(" ")[0]
                if store not in ids:
                    ids.append(store)
                    name = name.replace('"', "'")
                    add = add.replace('"', "'")
                    name = name.replace('"', "'")
                    if "12 Street West & Joanne" in add:
                        city = "Brooks"
                        add = "12 Street West & Joanne Trucking Rd"
                        state = "AB"
                        zc = "T1R 1C8"
                    if "7913 - 100 Avenue" in add:
                        add = "7913 - 100 Avenue"
                        city = "Peace River"
                        state = "AB"
                        zc = "T8S 1M5"
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

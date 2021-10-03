from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import html
import datetime
import time
from tenacity import retry, stop_after_attempt
import tenacity

MISSING = SgRecord.MISSING
DOMAIN = "dominos.com"
MAX_WORKERS = 16
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_com")

letters = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]


searchurls = [
    "CANADA|https://order.dominos.ca/store-locator-international/locate/store?regionCode=CA&latitude=43.653226&longitude=-79.3831843&radius=9999999",
    "BRAZIL|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=BR&latitude=-13.5415477&longitude=-56.3346976&radius=9999999",
    "ARUBA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=AW&latitude=12.5175281&longitude=-70.0357333&radius=9999999",
    "CAYMAN_ISLANDS|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=KY&latitude=19.3300248&longitude=-81.3224693&radius=9999999",
    "COLOMBIA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=CO&latitude=4.5709&longitude=-74.2973&Radius=1250000&radius=9999999",
    "DOMINICAN_REPUBLIC|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=DO&latitude=19.022717&longitude=-70.998641&radius=9999999",
    "ECUADOR|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=EC&latitude=-0.177491&longitude=-78.599166&radius=9999999",
    "GUATEMALA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=GT&latitude=15.3430079&longitude=-90.0663352&radius=9999999",
    "PANAMA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=PA&latitude=8.3999404&longitude=-80.6812235&radius=9999999",
    "ST_KITTS|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=KN&latitude=17.3021931&longitude=-62.7323442&radius=9999999",
    "ST_LUCIA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=LC&latitude=13.909444&longitude=-60.97889299999997&radius=9999999",
    "ST_MAARTEN|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=SX&latitude=18.0472401&longitude=-63.0887697&radius=9999999",
    "TRINIDAD|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=TT&latitude=10.536421&longitude=-61.311951&radius=9999999",
    "AUSTRIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=AT&latitude=48.262853&longitude=16.399944&radius=9999999",
    "CZECH_REPUBLIC|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=CZ&latitude=49.1938084&longitude=16.6076158&radius=9999999",
    "ITALY|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=IT&latitude=45.4654219&longitude=9.18592430000001&radius=9999999",
    "KOSOVO|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=XK&latitude=42.665411916980034&longitude=21.158615201711655&radius=9999999",
    "PORTUGAL|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=PT&latitude=38.740335&longitude=-9.1833424&radius=9999999",
    "SLOVAKIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=SK&latitude=48.14816&longitude=17.10674&radius=9999999",
    "SWEDEN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=SE&latitude=55.5700886&longitude=12.8758906&radius=9999999",
    "UAE|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=AE&latitude=25.234213&longitude=55.235698&radius=9999999",
    "CAMBODIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=KH&latitude=12.2927611&longitude=103.8567493&radius=9999999",
    "GUAM|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=GU&latitude=13.444304&longitude=144.79373099999998&radius=9999999",
    "PHILIPPINES|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=PH&latitude=14.599512&longitude=120.984222&Radius=2500&radius=9999999",
    "THAILAND|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=TH&latitude=13.499307&longitude=100.511436&radius=9999999",
    "BAHRAIN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=BH&latitude=26.250747&longitude=50.665052&radius=9999999",
    "EGYPT|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=EG&latitude=26.820553&longitude=30.802498000000014&radius=9999999",
    "JORDAN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=JO&latitude=32.2831971&longitude=35.8949949&radius=9999999",
    "LEBANON|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=LB&latitude=33.8886289&longitude=35.49547940000002&radius=9999999",
    "MAURITIUS|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=MU&latitude=-20.3484&longitude=57.5522&radius=9999999",
    "OMAN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=OM&latitude=20.391015&longitude=56.8505923&radius=9999999",
    "QATAR|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=QA&latitude=25.4477038&longitude=51.1814573&radius=9999999",
]

nlcities = [
    "Amsterdam",
    "Rotterdam",
    "The Hague",
    "Utrecht",
    "Eindhoven",
    "Groningen",
    "Tilburg",
    "Almere",
    "Breda",
    "Nijmegen",
    "Apeldoorn",
    "Haarlem",
    "Arnhem",
    "Enschede",
    "Amersfoort",
    "Zaanstad",
    "Haarlemmermeer",
    "Den Bosch",
    "Zwolle",
    "Zoetermeer",
    "Leiden",
    "Leeuwarden",
    "Maastricht",
    "Dordrecht",
    "Ede",
    "Alphen aan den Rijn",
    "Westland",
    "Alkmaar",
    "Emmen",
    "Delft",
    "Venlo",
    "Deventer",
    "Sittard Geleen",
    "Helmond",
    "Oss",
    "Amstelveen",
    "Hilversum",
    "Sudwest Fryslan",
    "Heerlen",
    "Hoeksche Waard",
    "Nissewaard",
    "Meierijstad",
    "Hengelo",
    "Purmerend",
    "Schiedam",
    "Lelystad",
    "Roosendaal",
    "Leidschendam Voorburg",
    "Gouda",
    "Hoorn",
    "Almelo",
    "Vlaardingen",
    "Velsen",
    "Assen",
    "Capelle aan den IJssel",
    "Bergen op Zoom",
    "Veenendaal",
    "Katwijk",
    "Stichtse Vecht",
    "Zeist",
    "Nieuwegein",
    "Westerkwartier",
    "Lansingerland",
    "Midden Groningen",
    "Hardenberg",
    "Roermond",
    "Barneveld",
    "Gooise Meren",
    "Doetinchem",
    "Heerhugowaard",
    "Krimpenerwaard",
    "Smallingerland",
    "Vijfheerenlanden",
    "Hoogeveen",
    "Oosterhout",
    "Den Helder",
    "Altena",
    "Terneuzen",
    "Pijnacker Nootdorp",
    "Kampen",
    "Rijswijk",
    "Woerden",
    "De Fryske Marren",
    "West Betuwe",
    "Heerenveen",
    "Houten",
    "Weert",
    "Goeree Overflakkee",
    "Utrechtse Heuvelrug",
    "Barendrecht",
    "Middelburg",
    "Waalwijk",
    "Het Hogeland",
    "Hollands Kroon",
    "Zutphen",
    "Harderwijk",
    "Overbetuwe",
    "Noordoostpolder",
    "Schagen",
    "Lingewaard",
]
dkcities = [
    "Copenhagen",
    "Aarhus",
    "Odense",
    "Aalborg",
    "Esbjerg",
    "Randers",
    "Kolding",
    "Horsens",
    "Vejle",
    "Roskilde",
    "Herning",
    "Horsholm",
    "Helsingor",
    "Silkeborg",
    "Naestved",
    "Fredericia",
    "Viborg",
    "Koge",
    "Holstebro",
    "Taastrup",
    "Slagelse",
    "Hillerod",
    "Holbaek",
    "Sonderborg",
    "Svendborg",
    "Hjorring",
    "Frederikshavn",
    "Norresundby",
    "Ringsted",
    "Haderslev",
    "Olstykke-Stenlose",
    "Skive",
    "Birkerod",
    "Farum",
    "Smorumnedre",
    "Skanderborg",
    "Nuuk",
    "Nyborg",
    "Nykobing F",
    "Lillerod",
    "Kalundborg",
    "Frederikssund",
    "Aabenraa",
    "Solrod Strand",
    "Ikast",
    "Middelfart",
    "Grenaa",
    "Korsor",
    "Varde",
    "Ronne",
    "Thisted",
    "Vaerlose",
    "Torshavn",
    "Nakskov",
    "Bronderslev",
    "Frederiksvaerk",
    "Dragor",
    "Vordingborg",
    "Hedehusene",
    "Hobro",
    "Odder",
    "Hedensted",
    "Haslev",
    "Lystrup",
    "Struer",
    "Jyllinge",
    "Ringkobing",
    "Grindsted",
    "Vejen",
    "Humlebaek",
    "Nykobing M",
    "Saeby",
    "Hundested",
    "Fredensborg St.by",
    "Beder-Malling",
    "Galten",
    "Ribe",
    "Aars",
    "Helsinge",
    "Hadsten",
    "Skagen",
    "Niva",
    "Soro",
    "Logten",
    "Skjern",
    "Horning",
    "Tonder",
    "Hinnerup",
    "Vojens",
    "Bjerringbro",
    "Stovring",
    "Ebeltoft",
    "Svenstrup",
    "Brande",
    "Bramming",
    "Faaborg",
    "Hammel",
    "Lemvig",
    "Slangerup",
    "Gilleleje",
]
frcities = [
    "Paris",
    "Marseille",
    "Lyon",
    "Toulouse",
    "Nice",
    "Nantes",
    "Strasbourg",
    "Montpellier",
    "Bordeaux",
    "Lille",
    "Rennes",
    "Reims",
    "Le Havre",
    "Saint Etienne",
    "Toulon",
    "Grenoble",
    "Dijon",
    "Nimes",
    "Angers",
    "Villeurbanne",
    "Le Mans",
    "Aix en Provence",
    "Clermont Ferrand",
    "Brest",
    "Tours",
    "Limoges",
    "Amiens",
    "Perpignan",
    "Metz",
    "Boulogne Billancourt",
    "Besancon",
    "Orleans",
    "Mulhouse",
    "Saint Denis",
    "Rouen",
    "Argenteuil",
    "Caen",
    "Montreuil",
    "Nancy",
    "Roubaix",
    "Tourcoing",
    "Nanterre",
    "Avignon",
    "Vitry sur Seine",
    "Creteil",
    "Dunkirk",
    "Poitiers",
    "Asnieres sur Seine",
    "Versailles",
    "Courbevoie",
    "Colombes",
    "Aulnay sous Bois",
    "Cherbourg en Cotentin",
    "Aubervilliers",
    "Rueil Malmaison",
    "Pau",
    "Champigny sur Marne",
    "Calais",
    "Antibes",
    "Beziers",
    "Saint Maur des Fosses",
    "La Rochelle",
    "Cannes",
    "Saint Nazaire",
    "Merignac",
    "Drancy",
    "Colmar",
    "Ajaccio",
    "Issy les Moulineaux",
    "Bourges",
    "Levallois Perret",
    "La Seyne sur Mer",
    "Noisy le Grand",
    "Quimper",
    "Cergy",
    "Villeneuve dAscq",
    "Venissieux",
    "Valence",
    "Neuilly sur Seine",
    "Antony",
    "Pessac",
    "Troyes",
    "Ivry sur Seine",
    "Clichy",
    "Chambery",
    "Montauban",
    "Niort",
    "Villejuif",
    "Lorient",
    "Sarcelles",
    "Hyeres",
    "Saint Quentin",
    "Epinay sur Seine",
    "Pantin",
    "Maisons Alfort",
    "Beauvais",
    "Le Blanc Mesnil",
    "Cholet",
    "Chelles",
    "Evry",
    "Meaux",
    "Frejus",
    "Annecy",
    "Fontenay sous Bois",
    "La Roche sur Yon",
    "Bondy",
    "Vannes",
    "Narbonne",
    "Arles",
    "Clamart",
    "Sartrouville",
    "Bobigny",
    "Grasse",
    "Sevran",
    "Laval",
    "Belfort",
    "Albi",
    "Evreux",
    "Corbeil Essonnes",
    "Vincennes",
    "Montrouge",
    "Martigues",
    "Charleville Mezieres",
    "Suresnes",
    "Massy",
    "Bayonne",
    "Cagnes sur Mer",
    "Saint Ouen",
    "Brive la Gaillarde",
    "Blois",
    "Saint Malo",
    "Carcassonne",
    "Meudon",
    "Vaulx en Velin",
    "Saint Brieuc",
    "Aubagne",
    "Alfortville",
    "Chalons en Champagne",
    "Chalon sur Saone",
    "Mantes la Jolie",
    "Puteaux",
    "Chateauroux",
    "Rosny sous Bois",
    "Saint Priest",
    "Saint Herblain",
    "Salon de Provence",
    "Sete",
    "Livry Gargan",
    "Valenciennes",
    "Istres",
]

decities = [
    "Berlin",
    "Hamburg",
    "Munich",
    "Cologne",
    "Frankfurt am Main",
    "Stuttgart",
    "Dusseldorf",
    "Dortmund",
    "Essen",
    "Leipzig",
    "Bremen",
    "Dresden",
    "Hanover",
    "Nuremberg",
    "Duisburg",
    "Bochum",
    "Wuppertal",
    "Bielefeld",
    "Bonn",
    "Munster",
    "Karlsruhe",
    "Mannheim",
    "Augsburg",
    "Wiesbaden",
    "Monchengladbach",
    "Gelsenkirchen",
    "Braunschweig",
    "Kiel",
    "Chemnitz",
    "Aachen",
    "Halle",
    "Magdeburg",
    "Freiburg im Breisgau",
    "Krefeld",
    "Lubeck",
    "Mainz",
    "Erfurt",
    "Oberhausen",
    "Rostock",
    "Kassel",
    "Hagen",
    "Saarbrucken",
    "Hamm",
    "Potsdam",
    "Mulheim an der Ruhr",
    "Ludwigshafen am Rhein",
    "Oldenburg",
    "Osnabruck",
    "Leverkusen",
    "Heidelberg",
    "Solingen",
    "Darmstadt",
    "Herne",
    "Neuss",
    "Regensburg",
    "Paderborn",
    "Ingolstadt",
    "Offenbach am Main",
    "Wurzburg",
    "Furth",
    "Ulm",
    "Heilbronn",
    "Pforzheim",
    "Wolfsburg",
    "Gottingen",
    "Bottrop",
    "Reutlingen",
    "Koblenz",
    "Recklinghausen",
    "Bremerhaven",
    "Bergisch Gladbach",
    "Jena",
    "Erlangen",
    "Remscheid",
    "Trier",
    "Salzgitter",
    "Moers",
    "Siegen",
    "Hildesheim",
    "Cottbus",
    "Kaiserslautern",
    "Gutersloh",
    "Witten",
    "Hanau",
    "Schwerin",
    "Gera",
    "Ludwigsburg",
    "Esslingen am Neckar",
    "Iserlohn",
    "Duren",
    "Zwickau",
    "Tubingen",
    "Flensburg",
    "Giessen",
    "Ratingen",
    "Lunen",
    "Villingen Schwenningen",
    "Konstanz",
    "Marl",
    "Worms",
]
nzcities = [
    "Auckland",
    "Christchurch",
    "Wellington",
    "Hamilton",
    "Tauranga",
    "Dunedin",
    "Lower Hutt",
    "Palmerston North",
    "Hastings",
    "Nelson",
    "Napier",
    "Rotorua",
    "New Plymouth",
    "Porirua",
    "Whangarei",
    "Invercargill",
    "Kapiti",
    "Wanganui",
    "Upper Hutt",
    "Gisborne",
    "Blenheim",
    "Timaru",
    "Pukekohe",
    "Taupo",
    "Masterton",
    "Levin",
    "Ashburton",
    "Whakatane",
    "Cambridge",
    "Te Awamutu",
    "Rangiora",
    "Feilding",
    "Oamaru",
    "Tokoroa",
    "Queenstown",
    "Hawera",
    "Greymouth",
    "Rolleston",
    "Gore",
    "Waiuku",
    "Waiheke Island",
    "Motueka",
    "Te Puke",
    "Matamata",
    "Morrinsville",
    "Huntly",
    "Thames",
    "Kerikeri",
    "Waitara",
    "Wanaka",
    "Kawerau",
    "Otaki",
    "Stratford",
    "Dannevirke",
    "Avarua",
    "Kaitaia",
    "Alexandra",
    "Carterton",
    "Marton",
    "Waihi",
    "Taumarunui",
    "Whitianga",
    "Foxton",
    "Dargaville",
    "Snells Beach",
    "Te Kuiti",
    "Cromwell",
    "Katikati",
    "Picton",
    "Wairoa",
    "Temuka",
    "Westport",
    "Lincoln",
    "Balclutha",
    "Kaikohe",
    "Warkworth",
    "Te Aroha",
    "Paeroa",
    "Opotiki",
    "Putaruru",
    "Waipukurau",
    "Whangamata",
    "Hokitika",
    "Inglewood",
    "Turangi",
    "Waimate",
    "Woodend",
    "Raglan",
    "Helensville",
    "Arorangi",
    "Otorohanga",
    "Arrowtown",
    "Pahiatua",
    "Geraldine",
    "Featherston",
    "Winton",
    "Greytown",
    "Wakefield",
    "Mapua",
    "Kaikoura",
]


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def fetch_records_global(idx, url, sgw: SgWriter):
    with SgRequests() as http:
        lurl = url.split("|")[1]
        cc = url.split("|")[0]
        headers2 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "DPZ-Market": cc,
        }

        r = http.get(lurl, headers=headers2)
        time.sleep(2)
        website = "dominos.com"
        typ = MISSING
        country = lurl.split("regionCode=")[1].split("&")[0]
        loc = MISSING
        store = MISSING
        hours = MISSING
        lat = MISSING
        lng = MISSING
        logger.info("Pulling Stores")
        for idx2, item in enumerate(json.loads(r.content)["Stores"][0:]):
            if "StoreName" in str(item):
                name = item["StoreName"]
            else:
                name = MISSING

            store = item["StoreID"]
            phone = ""
            if "Phone" in item:
                phone = item["Phone"]
            else:
                phone = MISSING
            phone = phone if phone else MISSING
            logger.info(f"[{idx}][{cc}][{idx2}] phone: {phone}")
            try:
                add = item["StreetName"]
            except:
                add = MISSING
            add = str(add).replace("\r", "").replace("\n", "")
            city = ""
            if "City" in item:
                city = str(item["City"]).replace("\r", "").replace("\n", "")
            else:
                city = MISSING
            city = city if city else MISSING

            state = ""
            if "Region" in item:
                state = item["Region"] if item["Region"] else MISSING
            else:
                state = MISSING

            zc = ""
            if "PostalCode" in item:
                zc = item["PostalCode"]
            else:
                zc = MISSING
            zc = zc if zc else MISSING

            if (
                "StoreCoordinates" in item
                and "StoreLatitude" in item["StoreCoordinates"]
            ):
                lat = item["StoreCoordinates"]["StoreLatitude"]
                lng = item["StoreCoordinates"]["StoreLongitude"]
            elif "Latitude" in item:
                lat = item["Latitude"]
                lng = item["Longitude"]
            else:
                lat = MISSING
                lng = MISSING

            logger.info(f"[{idx}][{cc}][{idx2}] Latlng: {lat} | {lng}")

            hours = ""
            if "HoursDescription" in item:
                hours = (
                    str(item["HoursDescription"])
                    .replace("\t", "")
                    .replace("\n", "; ")
                    .replace("\r", "")
                )
            else:
                hours = MISSING
            hours = hours if hours else MISSING

            loc = MISSING
            raw_address = MISSING

            if MISSING not in store and country == "CA":
                name = "STORE #" + store

            rec = SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
                raw_address=raw_address,
            )
            sgw.write_row(rec)


def get_open_close_times(d):
    opentime = d["Open"]
    closetime = d["Close"]
    op1 = datetime.datetime.strptime(opentime, "%Y-%m-%dT%H:%M:%S")
    cl1 = datetime.datetime.strptime(closetime, "%Y-%m-%dT%H:%M:%S")
    op_datetime_format = "%A: %H:%M"
    cl_datetime_format = "%H:%M"
    opentime_convert = op1.strftime(op_datetime_format)
    closetime_convert = cl1.strftime(cl_datetime_format)
    opcltime = opentime_convert + " - " + closetime_convert
    return opcltime


def get_limited_store_urls():
    city_based_urls = []
    urls = [
        "https://www.dominos.nl/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.dk/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.fr/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.de/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.co.nz/dynamicstoresearchapi/getlimitedstores/100/",
    ]
    for url in urls:
        alllocs = letters
        if ".de/" in url:
            alllocs = decities
        if ".fr/" in url:
            alllocs = frcities
        if ".dk/" in url:
            alllocs = dkcities
        if ".nl/" in url:
            alllocs = nlcities + letters
        if ".nz/" in url:
            alllocs = nzcities
        for letter in alllocs:
            cabb = url.split("/dynamic")[0].rsplit(".", 1)[1]
            logger.info("Pulling Letter %s, Country %s" % (letter, cabb))
            curl = url + letter
            city_based_urls.append(curl)
    return city_based_urls


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def fetch_records_eu_global(idx, curl, sgw: SgWriter):
    with SgRequests() as http:
        logger.info(f"Pulling from: {curl}")
        r = http.get(curl, headers=headers)
        time.sleep(3)
        website = "dominos.com"
        typ = MISSING
        country = ""
        loc = MISSING
        store = MISSING
        hours = MISSING
        lat = MISSING
        lng = MISSING

        if r.status_code == 200:
            for idx3, item in enumerate(json.loads(r.content)["Data"][0:]):
                name = item["Name"]
                store = item["StoreNo"]
                phone = item["PhoneNo"]
                phone = phone if phone else MISSING

                try:
                    a1 = str(item["Address"]["UnitNo"])
                except:
                    a1 = ""
                try:
                    a2 = str(item["Address"]["StreetNo"])
                except:
                    a2 = ""
                try:
                    a3 = str(item["Address"]["StreetName"])
                except:
                    a3 = ""
                add = a1 + " " + a2 + " " + a3
                add = add.strip().replace("  ", " ")
                add = add.replace("None ", "")
                add1 = " ".join(add.split()).replace("<Br/>", ", ").rstrip(",")
                city = item["Address"]["Suburb"] or MISSING
                state = ""
                if "State" in item["Address"]:
                    state = (
                        item["Address"]["State"]
                        if item["Address"]["State"]
                        else MISSING
                    )
                else:
                    state = MISSING
                zc = item["Address"]["PostalCode"] or MISSING
                logger.info(f"[{idx}][{idx3}] City: {city} | State: {state} | ZC: {zc}")

                lat = item["GeoCoordinates"]["Latitude"] or MISSING
                lng = item["GeoCoordinates"]["Longitude"] or MISSING

                openinghours = item["OpeningHours"]
                hoo = []
                for oh in openinghours:
                    oc = get_open_close_times(oh)
                    hoo.append(oc)
                hours = "; ".join(hoo)
                loc = MISSING
                country = item["CountryCode"] or MISSING
                raw_address = ""
                if "FullAddress" in item["Address"]:
                    fadd = item["Address"]["FullAddress"]
                    if fadd:
                        raw_address = (
                            " ".join(fadd.split()).replace("<Br/>", ", ").rstrip(",")
                        )
                    else:
                        raw_address = MISSING
                else:
                    raw_address = MISSING

                rec = SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=add1,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                    raw_address=raw_address,
                )

                sgw.write_row(rec)


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def get_us_store_urls():
    with SgRequests() as http:
        locs = []
        states = []
        url = "https://pizza.dominos.com/sitemap.xml"
        r = http.get(url, headers=headers)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines():
            if "https://pizza.dominos.com/" in line and "/home/sitemap" not in line:
                states.append(
                    line.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                )
        for state in states:
            Found = True
            logger.info(("Pulling State %s..." % state))
            r2 = http.get(state, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines():
                if "https://pizza.dominos.com/" in line2:
                    if line2.count("/") == 4:
                        Found = False
                    if Found:
                        locs.append(
                            line2.replace("\r", "")
                            .replace("\n", "")
                            .replace("\t", "")
                            .strip()
                        )
            logger.info(("%s Locations Found..." % str(len(locs))))
        return locs


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def fetch_records_us(idx, loc, sgw: SgWriter):
    with SgRequests() as http:
        r2 = http.get(loc, headers=headers)
        if r2.status_code == 200:
            sel = html.fromstring(r2.text, "lxml")
            raw_data = sel.xpath(
                '//script[contains(@type, "application/ld+json") and contains(text(), "LocalBusiness")]/text()'
            )
            raw_data1 = "".join(raw_data)
            try:
                json_data = json.loads(raw_data1)
            except json.decoder.JSONDecodeError:
                return
            page_url = json_data["url"]
            logger.info(f"[{idx}][US] PU: {page_url}")
            location_name = json_data["name"] or MISSING
            address = json_data["address"]
            street_address = address["streetAddress"] or MISSING
            city = address["addressLocality"] or MISSING
            state = address["addressRegion"] or MISSING
            zip_postal = address["postalCode"] or MISSING
            country_code = "US"
            store_number = json_data["branchCode"] or MISSING

            phone = ""
            try:
                phone = json_data["telephone"]
            except:
                phone = MISSING

            location_type = "Store"
            latitude = json_data["geo"]["latitude"] or MISSING
            longitude = json_data["geo"]["longitude"] or MISSING
            locator_domain = DOMAIN

            # Hours of Operation
            hoo = []
            for i in json_data["openingHoursSpecification"]:
                day_of_week = (
                    i["dayOfWeek"].replace("http://schema.org/", "")
                    + " "
                    + str(i["opens"] or "")
                    + " - "
                    + str(i["closes"] or "")
                )
                hoo.append(day_of_week)
            hours_of_operation = "; ".join(hoo)
            raw_address = MISSING
            location_name = location_name + " #" + str(store_number)
            rec = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )
            sgw.write_row(rec)


def fetch_data(sgw: SgWriter):

    us_store_urls = get_us_store_urls()
    eu_api_endpoint_urls_be = get_limited_store_urls()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_us = [
            executor.submit(fetch_records_us, unum, url, sgw)
            for unum, url in enumerate(us_store_urls[0:])
        ]
        tasks.extend(task_us)
        task_eu = [
            executor.submit(fetch_records_eu_global, unum, url, sgw)
            for unum, url in enumerate(eu_api_endpoint_urls_be[0:])
        ]
        tasks.extend(task_eu)
        task_global = [
            executor.submit(fetch_records_global, unum, url, sgw)
            for unum, url in enumerate(searchurls[0:])
        ]
        tasks.extend(task_global)
        for future in as_completed(tasks):
            future.result()


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STORE_NUMBER, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog
import json

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
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
    "BRAZIL|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=BR&latitude=-13.5415477&longitude=-56.3346976",
    "ARUBA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=AW&latitude=12.5175281&longitude=-70.0357333",
    "CAYMAN_ISLANDS|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=KY&latitude=19.3300248&longitude=-81.3224693",
    "COLOMBIA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=CO&latitude=4.5709&longitude=-74.2973&Radius=1250000",
    "DOMINICAN_REPUBLIC|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=DO&latitude=19.022717&longitude=-70.998641",
    "ECUADOR|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=EC&latitude=-0.177491&longitude=-78.599166",
    "GUATEMALA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=GT&latitude=15.3430079&longitude=-90.0663352",
    "PANAMA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=PA&latitude=8.3999404&longitude=-80.6812235",
    "ST_KITTS|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=KN&latitude=17.3021931&longitude=-62.7323442",
    "ST_LUCIA|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=LC&latitude=13.909444&longitude=-60.97889299999997",
    "ST_MAARTEN|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=SX&latitude=18.0472401&longitude=-63.0887697",
    "TRINIDAD|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=TT&latitude=10.536421&longitude=-61.311951",
    "AUSTRIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=AT&latitude=48.262853&longitude=16.399944",
    "CZECH_REPUBLIC|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=CZ&latitude=49.1938084&longitude=16.6076158",
    "ITALY|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=IT&latitude=45.4654219&longitude=9.18592430000001",
    "KOSOVO|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=XK&latitude=42.665411916980034&longitude=21.158615201711655",
    "PORTUGAL|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=PT&latitude=38.740335&longitude=-9.1833424",
    "SLOVAKIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=SK&latitude=48.14816&longitude=17.10674",
    "SWEDEN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=SE&latitude=55.5700886&longitude=12.8758906",
    "UAE|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=AE&latitude=25.234213&longitude=55.235698",
    "CAMBODIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=KH&latitude=12.2927611&longitude=103.8567493",
    "GUAM|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=GU&latitude=13.444304&longitude=144.79373099999998",
    "PHILIPPINES|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=PH&latitude=14.599512&longitude=120.984222&Radius=2500",
    "THAILAND|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=TH&latitude=13.499307&longitude=100.511436",
    "BAHRAIN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=BH&latitude=26.250747&longitude=50.665052",
    "EGYPT|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=EG&latitude=26.820553&longitude=30.802498000000014",
    "JORDAN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=JO&latitude=32.2831971&longitude=35.8949949",
    "LEBANON|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=LB&latitude=33.8886289&longitude=35.49547940000002",
    "MAURITIUS|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=MU&latitude=-20.3484&longitude=57.5522",
    "OMAN|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=OM&latitude=20.391015&longitude=56.8505923",
    "QATAR|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=QA&latitude=25.4477038&longitude=51.1814573",
    "SAUDI_ARABIA|https://www.dominos.sa/ar/pages/order/#!/locations/search/",
]


def fetch_data():
    urls = [
        "https://www.dominos.nl/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.dk/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.fr/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.de/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.be/dynamicstoresearchapi/getlimitedstores/100/",
        "https://www.dominos.co.nz/dynamicstoresearchapi/getlimitedstores/100/",
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
    becities = [
        "Brussels",
        "Antwerp",
        "Gent",
        "Charleroi",
        "Liege",
        "Brugge",
        "Namur",
        "Leuven",
        "Mons",
        "Mechelen",
        "Aalst",
        "La Louviere",
        "Hasselt",
        "Sint Niklaas",
        "Kortrijk",
        "Oostende",
        "Tournai",
        "Genk",
        "Seraing",
        "Roeselare",
        "Mouscron",
        "Verviers",
        "Beveren",
        "Beringen",
        "Dendermonde",
        "Vilvoorde",
        "Turnhout",
        "Deinze",
        "Dilbeek",
        "Heist op den Berg",
        "Lokeren",
        "Sint Truiden",
        "Geel",
        "Braine lAlleud",
        "Herstal",
        "Halle",
        "Ninove",
        "Maasmechelen",
        "Waregem",
        "Brasschaat",
        "Grimbergen",
        "Mol",
        "Lier",
        "Chatelet",
        "Evergem",
        "Tienen",
        "Ieper",
        "Schoten",
        "Wavre",
        "Zaventem",
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

    for url in urls:
        alllocs = letters
        if ".be/" in url:
            alllocs = becities
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
            r = session.get(curl, headers=headers)
            website = "dominos.com"
            typ = "<MISSING>"
            country = ""
            loc = "<MISSING>"
            store = "<MISSING>"
            hours = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            logger.info("Pulling Stores")
            try:
                for item in json.loads(r.content)["Data"]:
                    name = item["Name"]
                    store = item["StoreNo"]
                    phone = item["PhoneNo"]
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
                    city = item["Address"]["Suburb"]
                    state = "<MISSING>"
                    zc = item["Address"]["PostalCode"]
                    lat = item["GeoCoordinates"]["Latitude"]
                    lng = item["GeoCoordinates"]["Longitude"]
                    hours = str(item["OpeningHours"])
                    loc = "<MISSING>"
                    country = item["CountryCode"]
                    yield SgRecord(
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
                    )
            except:
                pass

    for url in searchurls:
        lurl = url.split("|")[1]
        cc = url.split("|")[0]
        logger.info(cc)
        headers2 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "DPZ-Market": cc,
        }
        try:
            r = session.get(lurl, headers=headers2)
            website = "dominos.br"
            typ = "<MISSING>"
            country = lurl.split("regionCode=")[1].split("&")[0]
            loc = "<MISSING>"
            store = "<MISSING>"
            hours = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            logger.info("Pulling Stores")
            for item in json.loads(r.content)["Stores"]:
                if "StoreName" in str(item):
                    name = item["StoreName"]
                    store = item["StoreID"]
                    phone = item["Phone"]
                    try:
                        add = item["StreetName"]
                    except:
                        add = "<MISSING>"
                    add = str(add).replace("\r", "").replace("\n", "")
                    city = str(item["City"]).replace("\r", "").replace("\n", "")
                    state = "<MISSING>"
                    zc = item["PostalCode"]
                    try:
                        lat = item["StoreCoordinates"]["StoreLatitude"]
                        lng = item["StoreCoordinates"]["StoreLongitude"]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    hours = (
                        str(item["HoursDescription"])
                        .replace("\t", "")
                        .replace("\n", "")
                        .replace("\r", "")
                    )
                    loc = "<MISSING>"
                    yield SgRecord(
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
                    )
        except:
            pass

    locs = []
    states = []
    url = "https://pizza.dominos.com/sitemap.xml"
    country = "US"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "https://pizza.dominos.com/" in line and "/home/sitemap" not in line:
            states.append(
                line.replace("\r", "").replace("\n", "").replace("\t", "").strip()
            )
    for state in states:
        Found = True
        logger.info(("Pulling State %s..." % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
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
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"branchCode":"' in line2:
                store = line2.split('"branchCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                name = "Domino's #" + store
                website = "dominos.com"
                country = "US"
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                typ = "Store"
                hours = (
                    line2.split('"openingHours":["')[1]
                    .split('"]')[0]
                    .replace('","', "; ")
                )
                try:
                    phone = line2.split(',"telephone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                yield SgRecord(
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
                )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()

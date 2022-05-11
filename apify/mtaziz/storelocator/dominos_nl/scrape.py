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
import ssl
import random
from urllib.parse import urlparse


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


MISSING = SgRecord.MISSING
DOMAIN = "dominos.nl"
MAX_WORKERS = 10
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_nl")

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
# Space Replaced with - ( Dash )
nlcities = [i.replace(" ", "-").lower() for i in nlcities]

nl_api_url_p1 = "https://www.dominos.nl/dynamicstoresearchapi/getlimitedstores/100/"
dk_api_url_p1 = "https://www.dominos.dk/dynamicstoresearchapi/getlimitedstores/100/"
nz_api_url_p1 = "https://www.dominos.co.nz/dynamicstoresearchapi/getlimitedstores/100/"
fr_api_url_p1 = "https://www.dominos.fr/dynamicstoresearchapi/getlimitedstores/100/"
de_api_url_p1 = "https://www.dominos.de/dynamicstoresearchapi/getlimitedstores/100/"

nl_api_urls_based_on_letters = [nl_api_url_p1 + i.lower() for i in letters]
dk_api_urls_based_on_letters = [dk_api_url_p1 + i.lower() for i in letters]
nz_api_urls_based_on_letters = [nz_api_url_p1 + i.lower() for i in letters]
fr_api_urls_based_on_letters = [fr_api_url_p1 + i.lower() for i in letters]
de_api_urls_based_on_letters = [de_api_url_p1 + i.lower() for i in letters]


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            logger.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"[{idx}] | {url} >> HTTP Error Code: {response.status_code}")


# Letter based API URLs return most of stores data but some of the stores may be missing
# That's there are two ways to get all the data
# City based URLs and letter-based API ENDPOINT URLs which covers all the stores
# NOTE: `getlimitedstores/100` in this case, if 200 or 300 used it does not work
# I think 100 refers to the number of stores that might be return by the API call.
de_api_url_p1 = "https://www.dominos.de/dynamicstoresearchapi/getlimitedstores/100/"
de_api_urls_based_on_letters = [de_api_url_p1 + i.lower() for i in letters]

fr_api_url_p1 = "https://www.dominos.fr/dynamicstoresearchapi/getlimitedstores/100/"
fr_api_urls_based_on_letters = [fr_api_url_p1 + i.lower() for i in letters]


nl_api_url_p1 = "https://www.dominos.nl/dynamicstoresearchapi/getlimitedstores/100/"
nl_api_urls_based_on_letters = [nl_api_url_p1 + i.lower() for i in letters]

nz_api_url_p1 = "https://www.dominos.co.nz/dynamicstoresearchapi/getlimitedstores/100/"
nz_api_urls_based_on_letters = [nz_api_url_p1 + i.lower() for i in letters]


# Denmark
def get_api_urls_dk():
    # Letter based API endpoint URLs returns the data for all the stores in Denmark
    # Therefore, we don't need the city-based API Endpoint URLs.
    dk_api_url_p1 = "https://www.dominos.dk/dynamicstoresearchapi/getlimitedstores/100/"
    dk_api_urls_based_on_letters = [dk_api_url_p1 + i.lower() for i in letters]
    return dk_api_urls_based_on_letters


# France


def get_api_urls_fr():
    FR_STORE_LOCATOR = "https://www.dominos.fr/trouver-son-dominos"
    fr_domain = urlparse(FR_STORE_LOCATOR).netloc
    FR_API_ENDPOINT_URL = (
        f"https://{fr_domain}/dynamicstoresearchapi/getlimitedstores/100/"
    )
    r = get_response(0, FR_STORE_LOCATOR)
    sel = html.fromstring(r.text, "lxml")
    city_links = '//ul[contains(@class, "city-links")]/li/a/@href'
    region_links = '//li[contains(@class, "region-link")]/a/@href'
    city_list = sel.xpath(city_links)
    region_list = sel.xpath(region_links)
    city_list.extend(region_list)
    city_list = [i.split("/")[-1] for i in city_list]
    city_list = [FR_API_ENDPOINT_URL + i for i in city_list]
    city_list.extend(fr_api_urls_based_on_letters)
    return city_list


# Newzealand
def get_api_urls_nz():
    # This extracts the list of cities from store locator URL,
    # and forms the API Endpoint URLs.
    # Available cities listed on the store locator Page, does not
    # cover all the stores data, that's why we had to add letter based,
    # API Endpoint URLs, combination of letter-based and city-based,
    # API Endpoint URLs covers all stores data for this country

    NZ_STORE_LOCATOR = "https://www.dominos.co.nz/store-finder"
    nz_domain = urlparse(NZ_STORE_LOCATOR).netloc
    NZ_API_ENDPOINT_URL = (
        f"https://{nz_domain}/dynamicstoresearchapi/getlimitedstores/100/"
    )
    r = get_response(0, NZ_STORE_LOCATOR)
    sel = html.fromstring(r.text, "lxml")
    city_links = '//ul[contains(@class, "city-links")]/li/a/@href'
    city_list = sel.xpath(city_links)
    city_list = [i.split("/")[-1] for i in city_list]
    city_list = [NZ_API_ENDPOINT_URL + i for i in city_list]
    city_list.extend(nz_api_urls_based_on_letters)
    return city_list


# Germany
def get_api_urls_de():
    DE_STORE_LOCATOR = "https://www.dominos.de/store"
    de_domain = urlparse(DE_STORE_LOCATOR).netloc
    DE_API_ENDPOINT_URL = (
        f"https://{de_domain}/dynamicstoresearchapi/getlimitedstores/100/"
    )
    region_links = '//li[contains(@class, "region-link")]/a/@href'
    r = get_response(0, DE_STORE_LOCATOR)
    sel = html.fromstring(r.text, "lxml")
    region_list = sel.xpath(region_links)
    region_list = [i.split("/")[-1] for i in region_list]
    region_list = [DE_API_ENDPOINT_URL + i for i in region_list]
    region_list.extend(de_api_urls_based_on_letters)
    return region_list


# Netherlands


def get_api_urls_nl():
    # Netherlands Store locator page does not include the list of cities,
    # therefore, we have manually listed all the major cities as nlcities
    # above and then API Endpoint URLs formed based on cities.
    # Secondly, It is found that all city-based API URLs does not
    # return data for all the stores, so, letter-based API URLs are added.

    NL_STORE_LOCATOR = "https://www.dominos.nl/over-dominos/english-visitors"
    nl_domain = urlparse(NL_STORE_LOCATOR).netloc
    NL_API_ENDPOINT_URL = (
        f"https://{nl_domain}/dynamicstoresearchapi/getlimitedstores/100/"
    )
    city_based_urls = []
    for city in nlcities:
        api_url_city = f"{NL_API_ENDPOINT_URL}{city}"
        city_based_urls.append(api_url_city)
    city_based_urls.extend(nl_api_urls_based_on_letters)
    return city_based_urls


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


def fetch_records_eu_global(idx, curl, sgw: SgWriter):
    logger.info(f"Pulling from: {curl}")
    r3 = get_response(idx, curl)
    time.sleep(3)
    typ = MISSING
    country = ""
    store = MISSING
    hours = MISSING
    lat = MISSING
    lng = MISSING
    data_raw = json.loads(r3.content)
    data_json = data_raw["Data"]
    if data_json:
        for idx3, item in enumerate(data_json[0:]):
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
                    item["Address"]["State"] if item["Address"]["State"] else MISSING
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
                locator_domain=DOMAIN,
                page_url="<INACCESSIBLE>",
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


def fetch_data(sgw: SgWriter):

    # Denmark
    dk_urls = get_api_urls_dk()

    # Germany
    de_urls = get_api_urls_de()
    dk_urls.extend(de_urls)

    # France
    fr_urls = get_api_urls_fr()
    dk_urls.extend(fr_urls)
    # Netherlands
    nl_urls = get_api_urls_nl()
    dk_urls.extend(nl_urls)

    # Newzealand
    nz_urls = get_api_urls_nz()
    dk_urls.extend(nz_urls)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task_eu = [
            executor.submit(fetch_records_eu_global, unum, url, sgw)
            for unum, url in enumerate(dk_urls[0:])
        ]
        tasks.extend(task_eu)
        for future in as_completed(tasks):
            future.result()


def scrape():
    logger.info("Scraping Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

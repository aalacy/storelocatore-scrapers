from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


DOMAIN = "vans.co.uk"
logger = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

headers = {
    "Accept": "text/javascript, text/html, application/xml, text/xml, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,it;q=0.6",
    "Connection": "keep-alive",
    "Cookie": "Authsite=httpss%3A%2F%2Flocations.vans.com%2Findex.html; AppKey=CFCAC866-ADF8-11E3-AC4F-1340B945EC6E; W2GISM=93a73840fe2a469687d3e116d03ec4fa",
    "Referer": "https://locations.vans.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    "X-Prototype-Version": "1.7.2",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Content-Type": "application/json",
}


def parse_json(store):
    data = {}
    data["locator_domain"] = DOMAIN
    store_number = store["clientkey"]
    if str(store_number) == "None":
        store_number = MISSING
    data["store_number"] = store_number

    page_url = store["url"]
    if str(page_url) == "None":
        page_url = MISSING
    data["page_url"] = page_url
    data["location_name"] = store["name"]
    data["location_type"] = MISSING
    type_check = store["name"].lower()
    if "store" in str(type_check):
        data["location_type"] = "store"
    if "outlet" in str(type_check):
        data["location_type"] = "outlet"

    street_address = store["address1"]
    data["street_address"] = (
        street_address.replace("Partner Operated Store -", "")
        .replace("McArthurGlen Designer Outlet,", "")
        .replace("McArthurGlen Designer Outlet", "")
        .replace("The Style Outlet,", "")
        .replace("Livingston Deisnger Outlet", "")
        .replace("Outlet Franciacorta Village,", "")
        .replace("Clarks Village Outlet Shopping,", "")
        .replace("The Style Outlets Vicolungo,", "")
        .replace("The Style Outlets ", "")
        .replace("La Reggia Designer Outlet,", "")
        .replace("Mallorca Fashion Outlet,", "")
        .replace("C.C  Cuore Adriatico -", "")
        .replace("62012 Civitanova Marche MC, Italia", "")
        .replace("C.C.  Campania - Autostrada A1 -", "")
        .replace("- Località Aurno", "")
        .replace("C.C Centro Sicilia -", "")
        .replace(", 95045 Misterbianco", "")
    )
    data["city"] = store["city"]
    state = store["province"]
    if str(state) == "None":
        state = MISSING
    data["state"] = state
    country_code = store["country"]
    data["country_code"] = country_code
    zip_postal = store["postalcode"]
    if str(zip_postal) == "0" or str(zip_postal) == "None":
        zip_postal = MISSING
    data["zip_postal"] = zip_postal
    phone = store["phone"]
    if str(phone) == "None":
        phone = MISSING
    data["phone"] = phone
    data["latitude"] = store["latitude"]
    data["longitude"] = store["longitude"]
    days = {
        "m": "Monday",
        "t": "Tuesday",
        "w": "Wednesday",
        "thu": "Thursday",
        "f": "Friday",
        "sa": "Saturday",
        "su": "Sunday",
    }
    hoo = []
    for day in days.keys():
        try:
            hoo.append(days[day] + ": " + store[day].replace("\n", ","))
        except:
            hoo.append(days[day] + ": " + "<MISSING>")
    data["hours_of_operation"] = ", ".join(hoo)

    return data


def fetch_data():
    session = SgRequests()
    api_url = "https://locations.vans.com/01062013/where-to-get-it/rest/locatorsearch"
    querystring = {"like": "0.43291943371727326", "lang": "en_EN"}

    payload = {
        "request": {
            "appkey": "CFCAC866-ADF8-11E3-AC4F-1340B945EC6E",
            "formdata": {
                "atleast": 1,
                "dataview": "store_default",
                "false": "0",
                "geoip": "false",
                "geolocs": {
                    "geoloc": [
                        {
                            "address1": "11 Ringugnsgatan",
                            "addressline": "vista",
                            "city": "",
                            "country": "SE",
                            "latitude": 55.5743683,
                            "longitude": 12.9314212,
                            "postalcode": "216 16",
                            "province": "Skåne län",
                            "state": "",
                        }
                    ]
                },
                "order": "_DISTANCE",
                "searchradius": "5000",
                "where": {
                    "or": {
                        "aut": {"eq": ""},
                        "off": {"eq": "TRUE"},
                        "out": {"eq": "TRUE"},
                    }
                },
            },
        }
    }

    response = session.get(api_url, json=payload, headers=headers, params=querystring)
    data_json = response.json()

    for store in data_json["response"]["collection"]:
        country_code = store["country"]
        if (
            country_code == "CY"
            or country_code == "CA"
            or country_code == "US"
            or country_code == "IN"
            or country_code == "KR"
        ):
            continue

        yield parse_json(store)


def scrape():
    logger.info(f"Start Crawling {DOMAIN} ...")
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(DOMAIN),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["location_name"], is_required=False),
        latitude=sp.MappingField(mapping=["latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["longitude"], is_required=False),
        street_address=sp.MappingField(mapping=["street_address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip_postal"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["store_number"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

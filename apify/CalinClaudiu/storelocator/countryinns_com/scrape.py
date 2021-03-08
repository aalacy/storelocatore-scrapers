from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json
from requests import exceptions  # noqa
from sglogging import sglog
from sgrequests import SgRequests

logzilla = sglog.SgLogSetup().get_logger(logger_name="Radisson fam")


def para(tup):
    k = {}
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    try:
        try:
            if len(tup[1]) > 0:
                k = json.loads(
                    str(
                        next(
                            net_utils.fetch_xml(
                                root_node_name="body",
                                location_node_name="script",
                                location_node_properties={
                                    "type": "application/ld+json",
                                    "id": "schema-webpage",
                                },
                                request_url=tup[1],
                                headers=headers,
                            )
                        )["script type=application/ld+json id=schema-webpage"]
                    )
                    .replace("\u0119", "e")
                    .replace("\u011f", "g")
                    .replace("\u0144", "n")
                    .replace("\u0131", "i"),
                    strict=False,
                )  # ['script type=application/ld+json']).rsplit(';',1)[0])
                k["STATUS"] = True
            else:
                k["requrl"] = "<MISSING>"
                k["index"] = tup[0]
                k["STATUS"] = True
        except exceptions.RequestException as e:
            if "404" in str(e):
                k = {}
                k["STATUS"] = False
            else:
                logzilla.info(f"Exception: {e}")
                raise Exception
    except StopIteration:
        return

    k["index"] = tup[0]
    k["requrl"] = tup[1]
    return k


def clean_record(k):

    try:
        k["sub"] = k["sub"]
    except Exception:
        k["sub"] = {}
        k["sub"]["mainEntity"] = {}
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"
        k["sub"]["mainEntity"]["telephone"] = ["<MISSING>"]
        k["sub"]["mainEntity"]["@type"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"] = k["sub"]["mainEntity"]
    except Exception:
        k["sub"]["mainEntity"] = {}
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"
        k["sub"]["mainEntity"]["telephone"] = ["<MISSING>"]
        k["sub"]["mainEntity"]["@type"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"] = k["sub"]["mainEntity"]["address"]
    except Exception:
        k["sub"]["mainEntity"]["address"] = {}
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["streetAddress"] = k["sub"]["mainEntity"][
            "address"
        ]["streetAddress"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["streetAddress"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressLocality"] = k["sub"]["mainEntity"][
            "address"
        ]["addressLocality"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressLocality"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressRegion"] = k["sub"]["mainEntity"][
            "address"
        ]["addressRegion"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressRegion"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["postalCode"] = k["sub"]["mainEntity"][
            "address"
        ]["postalCode"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["postalCode"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["address"]["addressCountry"] = k["sub"]["mainEntity"][
            "address"
        ]["addressCountry"]
    except Exception:
        k["sub"]["mainEntity"]["address"]["addressCountry"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["telephone"] = k["sub"]["mainEntity"]["telephone"]
    except Exception:
        k["sub"]["mainEntity"]["telephone"] = "<MISSING>"

    try:
        k["sub"]["mainEntity"]["@type"] = k["sub"]["mainEntity"]["@type"]
    except Exception:
        k["sub"]["mainEntity"]["@type"] = ""

    try:
        k["main"] = k["main"]
    except Exception:
        k["main"] = {}
        k["main"]["coordinates"] = {}
        k["main"]["coordinates"]["latitude"] = "<MISSING>"
        k["main"]["coordinates"]["longitude"] = "<MISSING>"
        k["main"]["code"] = "<MISSING>"
        k["main"]["name"] = "<MISSING>"

    try:
        k["main"]["coordinates"] = k["main"]["coordinates"]
    except Exception:
        k["main"]["coordinates"] = {}
        k["main"]["coordinates"]["latitude"] = "<MISSING>"
        k["main"]["coordinates"]["longitude"] = "<MISSING>"

    try:
        k["main"]["code"] = k["main"]["code"]
    except Exception:
        k["main"]["code"] = "<MISSING>"

    try:
        k["main"]["name"] = k["main"]["name"]
    except Exception:
        k["main"]["name"] = "<MISSING>"

    return k


def get_brand(brand, humanBrand):
    logzilla.info(f"Selected brand: {brand}")
    # Brand selector
    url = "https://www.radissonhotels.com/zimba-api/destinations/hotels?brand=" + brand

    headers = {}
    headers["authority"] = "www.radissonhotels.com"
    headers["method"] = "GET"
    headers["path"] = "/zimba-api/destinations/hotels?brand=" + brand
    headers["scheme"] = "https"
    headers["accept"] = "application/json, text/plain, */*"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "en-us"
    headers["referer"] = "https://www.radissonhotels.com/en-us/destination"
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "same-origin"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"

    session = SgRequests()
    resp = session.get(url, headers=headers).json()
    son = []
    son.append(resp)
    badrecords = []

    for i in son:
        k = i
        if len(k["hotels"]) != 0:
            if k["hotels"][0]["brand"] == brand:
                par = utils.parallelize(
                    search_space=[
                        [counter, z["overviewPath"]]
                        for counter, z in enumerate(k["hotels"])
                    ],
                    fetch_results_for_rec=para,
                    max_threads=20,
                    print_stats_interval=20,
                )
                for store in par:
                    if store and store["STATUS"]:
                        uscagb = 0
                        try:
                            if (
                                "Canada"
                                in store["mainEntity"]["address"]["addressCountry"]
                                or "United S"
                                in store["mainEntity"]["address"]["addressCountry"]
                                or "United King"
                                in store["mainEntity"]["address"]["addressCountry"]
                            ):
                                uscagb = 1
                            else:
                                logzilla.info(
                                    f"Ignoring hotel due to country not US/CA/UK: {store['mainEntity']['address']['addressCountry']}\n (for url -> {store['requrl']})"
                                )

                        except:
                            logzilla.info(f"Issues finding Country for record: {store}")
                            if len(list(store)) > 5:
                                logzilla.info(f"====================")  # noqa
                                logzilla.info(f"====================")  # noqa
                                logzilla.info(f"{store}")
                                logzilla.info(f"====================")  # noqa
                                logzilla.info(f"====================")  # noqa
                                raise Exception(
                                    "Crawler would've dropped this location above"
                                )
                            else:
                                badrecords.append(store)
                        if uscagb == 1:
                            try:
                                store["mainEntity"]["address"]["addressRegion"] = store[
                                    "mainEntity"
                                ]["address"]["addressRegion"]
                            except Exception:
                                store["mainEntity"]["address"]["addressRegion"] = ""
                            try:
                                store["mainEntity"]["@type"] = (
                                    humanBrand + " - " + store["mainEntity"]["@type"]
                                )
                            except Exception:
                                store["mainEntity"]["@type"] = (
                                    humanBrand if humanBrand else ""
                                )
                            yield clean_record(
                                {"main": k["hotels"][store["index"]], "sub": store}
                            )


def fetch_data():
    brands = [
        "pii",  # 0-Park Inn ###DONE
        "rdb",  # 1-Radisson Blu   ###DONE
        "rdr",  # 2-Radisson RED   ###DONE
        "art",  # 3-art'otel
        "rad",  # 4-Radisson Hotel ###DONE
        "ri",  # 5-Radisson Individuals
        "prz",  # 6-??? Empty
        "pph",  # 7-Park Plaza
        "cis",  # 8-Country Inn & Suites by Radisson ###DONE
        "rco",  # 9-Radisson Collection Paradise Resort
    ]
    brands = [
        {"code": "pii", "name": "Park Inn by Radisson"},
        {"code": "rdb", "name": "Radisson Blu"},
        {"code": "rdr", "name": "Radisson RED"},
        {"code": "art", "name": "art'otel"},
        {"code": "rad", "name": "Radisson"},
        {"code": "ri", "name": "Radisson Individuals"},
        {"code": "prz", "name": "prizeotel"},
        {"code": "pph", "name": "Park Plaza"},
        {"code": "cis", "name": "Country Inn & Suites"},
        {"code": "rco", "name": "Radisson Collection"},
    ]
    for brand in brands:
        for record in get_brand(brand["code"], brand["name"]):
            yield record

    logzilla.info(f"Finished grabbing data!!")  # noqa


def validatorsux(x):
    if x == "Wisconsin":
        x = "WI"
    if x == "Washington":
        x = "WA"
    if x == "West Virginia":
        x = "WV"
    if x == "Wyoming":
        x = "WY"
    return x


def scrape():
    url = "https://www.radissonhotels.com/en-us/destination"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["sub", "requrl"]),
        location_name=MappingField(mapping=["main", "name"]),
        latitude=MappingField(mapping=["main", "coordinates", "latitude"]),
        longitude=MappingField(mapping=["main", "coordinates", "longitude"]),
        street_address=MappingField(
            mapping=["sub", "mainEntity", "address", "streetAddress"]
        ),
        city=MappingField(mapping=["sub", "mainEntity", "address", "addressLocality"]),
        state=MappingField(
            mapping=["sub", "mainEntity", "address", "addressRegion"],
            value_transform=validatorsux,
            is_required=False,
        ),
        zipcode=MappingField(
            mapping=["sub", "mainEntity", "address", "postalCode"], is_required=False
        ),
        country_code=MappingField(
            mapping=["sub", "mainEntity", "address", "addressCountry"]
        ),
        phone=MappingField(mapping=["sub", "mainEntity", "telephone", 0]),
        store_number=MappingField(mapping=["main", "code"]),
        hours_of_operation=MissingField(),
        location_type=MappingField(mapping=["sub", "mainEntity", "@type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="radissonblu.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sglogging import sglog as loggie

logzilla = loggie.SgLogSetup().get_logger(logger_name="Scraper")

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_1_KM


def transform_item_map(raw, country):
    good = {}
    good["locator_domain"] = country
    good["location_name"] = raw["properties"]["name"]
    good["latitude"] = raw["geometry"]["coordinates"][-1]
    good["longitude"] = raw["geometry"]["coordinates"][0]
    good["street_address"] = ""
    try:
        raw["properties"]["addressLine1"] = raw["properties"]["addressLine1"]
        good["street_address"] = raw["properties"]["addressLine1"]
    except Exception:
        pass
    try:
        raw["properties"]["addressLine2"] = raw["properties"]["addressLine2"]
        good["street_address"] = (
            good["street_address"] + ", " + raw["properties"]["addressLine2"]
        )
    except Exception:
        pass
    good["street_address"] = fix_comma(good["street_address"])
    try:
        good["city"] = raw["properties"]["addressLine3"]
    except Exception:
        good["city"] = ""
    rightID = None
    for i in raw["properties"]["identifiers"]["storeIdentifier"]:
        if i["identifierType"] == "LocalRefNum":
            rightID = i["identifierValue"]
    good["page_url"] = "{}/location///{}.html".format(
        country.replace(".html", ""), str(rightID)
    )
    try:
        good["state"] = raw["properties"]["subDivision"]
    except Exception:
        pass
    try:
        good["zipcode"] = raw["properties"]["postcode"]
    except Exception:
        pass
    try:
        good["country_code"] = raw["properties"]["addressLine4"]
    except Exception:
        pass
    try:
        raw["properties"]["telephone"] = raw["properties"]["telephone"]
        good["phone"] = raw["properties"]["telephone"]
    except Exception:
        pass
    good["store_number"] = raw["properties"]["id"]
    try:
        good["hours_of_operation"] = str(raw["properties"]["restauranthours"]).replace(
            '"', " "
        )
        good["hours_of_operation"] = (
            good["hours_of_operation"]
            .replace("{", "")
            .replace("}", "")
            .replace("hours", "")
            .replace("'", "")
        )
    except Exception:
        pass
    try:
        good["location_type"] = (
            str(raw["properties"]["filterType"])
            .replace("'", "")
            .replace("[", "")
            .replace("]", "")
        )
    except Exception:
        pass
    good["raw_address"] = ""
    return good


def pull_map_poi(coord, url, session, locale, lang, country):
    lat, lng = coord
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    data = SgRequests.raise_on_err(
        session.get(
            url.format(lat=lat, lng=lng, locale=locale, lang=lang), headers=headers
        )
    ).json()
    for raw in data["features"]:
        good = transform_item_map(raw, country)
        yield good


def fetch_data():
    url = "https://www.mcdonalds.com/googleappsv2/geolocation?latitude={lat}&longitude={lng}&radius=300&maxResults=250&country=fi&language=fi-fi&showClosed=&hours24Text=Open%2024%20hr"
    url = "https://www.mcdonalds.com/googleappsv2/geolocation?latitude={lat}&longitude={lng}&radius=300&maxResults=250&country={locale}&language={lang}&showClosed=&hours24Text=Open%2024%20hr"
    locale = "fi"
    lang = "fi-fi"
    lang2 = lang.split("-")[1]
    lang2 = "en-" + lang
    try:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.FINLAND],
            granularity=Grain_1_KM(),
        )
    except Exception as e:
        logzilla.warning("", exc_info=e)
    country = "https://www.mcdonalds.com/fi/fi-fi.html"
    if search:
        with SgRequests(proxy_country=locale) as session2:
            for coord in search:
                try:
                    for rec in pull_map_poi(
                        coord, url, session2, locale, lang, country
                    ):
                        search.found_location_at(rec["latitude"], rec["longitude"])
                        yield rec
                except Exception as e:
                    logzilla.error(f"dropped_record @ \n{str(coord)}", exc_info=e)
                    pass
                try:
                    for rec in pull_map_poi(
                        coord, url, session2, locale, lang2, country
                    ):
                        search.found_location_at(rec["latitude"], rec["longitude"])
                        yield rec
                except Exception as e:
                    logzilla.error(f"dropped_record @ \n{str(coord)}", exc_info=e)
                    pass
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.FINLAND], max_search_results=250
        )


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h).replace("  ", " ")
    except Exception:
        return x.replace("  ", " ")


def fix_storeno(x):
    better = []
    for i in x:
        if i.isdigit():
            better.append(i)
    return "".join(better)


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.MappingField(
            mapping=["locator_domain"],
        ),
        page_url=sp.MappingField(
            mapping=["page_url"],
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["location_name"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
            is_required=False,
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(
            mapping=["street_address"],
            is_required=False,
            part_of_record_identity=True,
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zipcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country_code"], is_required=False),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["store_number"], is_required=False, value_transform=fix_storeno
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours_of_operation"], is_required=False
        ),
        location_type=sp.MappingField(mapping=["location_type"], is_required=False),
        raw_address=sp.MappingField(mapping=["raw_address"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=10,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgpostal.sgpostal import parse_address_intl


def para(k):
    session = SgRequests()
    # https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id=2479
    ide = k["id"]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    k = SgRequests.raise_on_err(
        session.get(
            "https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id="
            + k["id"],
            headers=headers,
        )
    )
    k = k.json()
    k = k["data"]
    rawa = k["address"]
    k["raw"] = rawa
    parsed = parse_address_intl(k["address"])
    k["zip"] = parsed.postcode if parsed.postcode else ""
    k["region"] = parsed.state if parsed.state else ""
    k["town"] = parsed.city if parsed.city else ""
    k["address"] = parsed.street_address_1 if parsed.street_address_1 else ""
    if parsed.street_address_2:
        k["address"] = k["address"] + parsed.street_address_2
    k["id"] = ide
    k["page_url"] = (
        "https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id="
        + k["id"]
    )
    return k


def fix_hours(x):
    x = x.replace("<br />", ", ").replace("\n", "").replace("\r", "").replace("\t", "")
    try:
        x = x.split("/2021")[1].strip()
    except Exception:
        pass
    return x


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.tntsupermarket.com/rest/V1/xmapi/get-store-list-new?lang=en&address={zipcode}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        expected_search_radius_miles=4,
        max_search_results=None,
    )
    identities = set()
    maxZ = search.items_remaining()
    total = 0
    with SgRequests() as session:
        for zipcode in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            found = 0
            son = session.get(url.format(zipcode=zipcode), headers=headers).json()
            son = son["data"]["filter_by_location"]["city_stores"]
            copy = []
            for i in son:
                for store in i:
                    search.found_location_at(store["lat"], store["lng"])
                    if store["id"] not in identities:
                        identities.add(store["id"])
                        found += 1
                        copy.append(store)
            if len(copy) > 0:

                son = copy

                lize = utils.parallelize(
                    search_space=son,
                    fetch_results_for_rec=para,
                    max_threads=20,
                    print_stats_interval=20,
                )
                for i in lize:
                    yield i
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )
            total += found
            logzilla.info(
                f"{zipcode} | found: {found} | total: {total} | progress: {progress}"
            )


def scrape():
    url = "https://www.tntsupermarket.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"], is_required=False),
        location_name=sp.MappingField(mapping=["name"], is_required=False),
        latitude=sp.MappingField(mapping=["lat"], is_required=False),
        longitude=sp.MappingField(mapping=["lng"], is_required=False),
        street_address=sp.MappingField(mapping=["address"], is_required=False),
        city=sp.MappingField(mapping=["town"], is_required=False),
        state=sp.MappingField(mapping=["region"], is_required=False),
        zipcode=sp.MappingField(mapping=["zip"], is_required=False),
        country_code=sp.MissingField(),
        phone=sp.MappingField(mapping=["phone"], is_required=False),
        store_number=sp.MappingField(mapping=["id"], part_of_record_identity=True),
        hours_of_operation=sp.MappingField(
            mapping=["store_hours"], value_transform=fix_hours, is_required=False
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(mapping=["raw"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawl",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

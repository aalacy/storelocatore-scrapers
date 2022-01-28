from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    backup = k
    try:
        k["zip"] = k["address"].rsplit(".", 1)[1]
        k["zip"] = k["zip"].strip()
    except:
        k["zip"] = "<MISSING>"

    try:
        k["region"] = k["address"].rsplit(".", 1)[0].rsplit(",", 1)[1]
        k["region"] = k["region"].strip()
    except:
        k["region"] = "<MISSING>"

    try:
        k["town"] = k["address"].split("  ", 1)[1].split(",")[0]
        k["town"] = k["town"].strip()
    except:
        k["town"] = "<MISSING>"

    try:
        addressbackup = k["address"]
        k["address"] = k["address"].split("  ", 1)[0]
    except:
        k["address"] = "<MISSING>"

    if k["town"] == "<MISSING>":
        try:
            k["address"] = k["address"].split("North Waterloo", 1)[0]
            k["town"] = "Waterloo"
        except:
            pass
    k["id"] = ide
    k["page_url"] = (
        "https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id="
        + k["id"]
    )

    if k["zip"] == "<MISSING>":
        k = backup
        try:
            k["zip"] = k["address"].rsplit(",", 1).split(" ")
            k["region"] = k["zip"][0]
            k["zip"] = "".join(k["zip"][1:])
        except:
            k["zip"] = "<MISSING>"

        try:
            k["town"] = k["address"].split("  ", 1)[1].split(",")[0]
            k["town"] = k["town"].strip()
        except:
            k["town"] = "<MISSING>"

        try:
            k["address"] = k["address"].split("  ", 1)[0]
        except:
            k["address"] = "<MISSING>"

        if k["town"] == "<MISSING>":
            try:
                k["address"] = k["address"].split("North Waterloo", 1)[0]
                k["town"] = "Waterloo"
            except:
                pass
        k["id"] = ide
        k["page_url"] = (
            "https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id="
            + k["id"]
        )
    if len(k["town"]) > len(k["address"]):
        k["address"] = addressbackup
        try:
            k["address"] = k["address"].split(")", 1)[1]
            k["address"] = k["address"].rsplit(",", 1)[0]
            k["town"] = k["address"].rsplit(" ", 1)[1]
            k["address"] = k["address"].replace(k["town"], "").replace("  ", " ")
        except Exception:
            k["address"] = addressbackup
            k["town"] = "<INACCESSIBLE>"
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
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["name"]),
        latitude=sp.MappingField(mapping=["lat"]),
        longitude=sp.MappingField(mapping=["lng"]),
        street_address=sp.MappingField(mapping=["address"]),
        city=sp.MappingField(mapping=["town"]),
        state=sp.MappingField(mapping=["region"]),
        zipcode=sp.MappingField(mapping=["zip"]),
        country_code=sp.MissingField(),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(mapping=["id"], part_of_record_identity=True),
        hours_of_operation=sp.MappingField(
            mapping=["store_hours"], value_transform=fix_hours
        ),
        location_type=sp.MissingField(),
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

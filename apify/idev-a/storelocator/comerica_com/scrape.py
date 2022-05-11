from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_1_KM
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
import json

logger = SgLogSetup().get_logger("comerica_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA], granularity=Grain_1_KM()
)


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    maxZ = search.items_remaining()
    total = 0
    for code in search:
        with SgRequests(proxy_country="us", retries_with_fresh_proxy_ip=7) as session:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            found = 0
            page = 1
            logger.info(("Pulling Zip Code %s..." % code))
            while True:
                url = f"https://locations.comerica.com/?q={code}&page={page}"
                try:
                    res = session.get(url, headers=headers).text
                except Exception:
                    logger.warning(f"^^^ get {url}")
                    break

                if "Comerica Bank is not in your area." in res:
                    logger.info(f"not found {code} | page {page} ")
                    break
                if "You have exceeded the maximum number of allowed searches." in res:
                    logger.info("Proxy not working")
                    break
                soup = bs(res, "lxml")
                try:
                    r2 = json.loads(
                        res.split("var results = ")[1]
                        .strip()
                        .split("var map;")[0]
                        .strip()[:-1]
                    )
                except:
                    logger.warning("^^^ load json")
                    break
                for _ in r2:
                    for store in _["location"]["entities"]:
                        store["state"] = _["location"]["province"]
                        store["city"] = _["location"]["city"]
                        store["street"] = _["location"]["street"]
                        store["country"] = _["location"]["country"]
                        store["lat"] = _["location"]["lat"]
                        store["lng"] = _["location"]["lng"]
                        store["postal_code"] = _["location"]["postal_code"]
                        if "name" in store:
                            name = "-".join(
                                [
                                    nn
                                    for nn in store.get("name")
                                    .lower()
                                    .replace(" - ", "-")
                                    .replace(" & ", "-")
                                    .replace(",", "")
                                    .replace(".", "")
                                    .replace("/", "")
                                    .replace("(", "")
                                    .replace(")", "")
                                    .split(" ")
                                    if nn.strip()
                                ]
                            )
                            store[
                                "page_url"
                            ] = f"https://locations.comerica.com/location/{name}"
                        elif store["type"] == "atm" and store["cma_id"]:
                            store["name"] = store["type"] + store["street"]
                            store[
                                "page_url"
                            ] = f"https://locations.comerica.com/location/{store['type'].lower()}-{store['cma_id'].lower()}"

                        else:
                            continue
                        store["hours"] = human_hours(store["open_hours_formatted"])
                        if "page_url" in store:
                            soup1 = bs(
                                session.get(store["page_url"], headers=headers).text,
                                "lxml",
                            )
                            h3_tag = soup1.select_one('h3[property="name"]')
                            try:
                                if h3_tag.find_next_sibling("p"):
                                    store["hours"] = "Temporarily closed"
                            except:
                                pass

                        yield store
                        found += 1
                total += found
                progress = (
                    str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
                )

                logger.info(
                    f"{code} | page {page} | found: {found} | total: {total} | progress: {progress}"
                )

                if soup.select_one("ul.pager li.next a"):
                    page = int(
                        soup.select_one("ul.pager li.next a")["href"].split("page=")[-1]
                    )
                else:
                    break


def human_phone(val):
    if val:
        return val.strip()
    else:
        return "<MISSING>"


def human_hours(k):
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    if k.get("lobby") or k.get("drive"):
        hours = []
        for x, _ in enumerate(k.get("lobby", []) or k.get("drive", [])):
            time = _
            if not _:
                time = "closed"
            hours.append(f"{days[x]}: {time}")
        return "; ".join(hours)
    else:
        return "<MISSING>"


def scrape():
    url = "https://www.comerica.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
        ),
        street_address=sp.MappingField(
            mapping=["street"],
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["state"],
        ),
        zipcode=sp.MappingField(
            mapping=["postal_code"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
            raw_value_transform=human_phone,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(
            mapping=["type"],
            part_of_record_identity=True,
        ),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
        duplicate_streak_failure_factor=100,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

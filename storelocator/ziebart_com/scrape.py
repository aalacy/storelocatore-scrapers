from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from bs4 import BeautifulSoup as bs
import re
from sgscrape.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("watchesofswitzerland")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ziebart.com"
base_url = "https://www.ziebart.com/find-my-ziebart?zipcode={}&distance=100"

search = DynamicZipSearch(
    country_codes=SearchableCountries.WITH_ZIPCODE_AND_COORDS,
    max_search_distance_miles=100,
)


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_data():
    # Need to add dedupe. Added it in pipeline.
    session = SgRequests(proxy_rotation_failure_threshold=20)
    maxZ = search.items_remaining()
    total = 0
    for zip in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % zip))
        locations = bs(
            session.get(base_url.format(zip), headers=_headers).text, "lxml"
        ).select("ul.sfStoreList li")
        total += len(locations)
        for _ in locations:
            store = {}
            store["page_url"] = locator_domain + _.h4.a["href"]
            store["name"] = _.h4.text.strip()
            addr = parse_address_intl(_.h3.text.strip())
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            store["street"] = street_address
            store["city"] = addr.city
            store["state"] = addr.state
            store["zip_postal"] = addr.postcode
            store["country"] = SgRecord.MISSING
            sp1 = bs(session.get(store["page_url"], headers=_headers).text, "lxml")
            hours = []
            _hr = sp1.find("h2", string=re.compile(r"Hours"))
            if _hr:
                for hh in _hr.find_parent().select("div.store-detail-text"):
                    hours.append(" ".join(hh.stripped_strings))
            try:
                coord = (
                    sp1.select("div.store-detail-left div.store-detail a")[1]["href"]
                    .split("/@")[1]
                    .split("/data")[0]
                    .split(",")
                )
                search.found_location_at(
                    coord[0],
                    coord[1],
                )
            except:
                coord = [SgRecord.MISSING, SgRecord.MISSING]
            store["lat"] = coord[0]
            store["lng"] = coord[1]
            store["hours"] = "; ".join(hours) or SgRecord.MISSING
            store["phone"] = _.select_one(".location-phone .phone-digits").text.strip()
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
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
            mapping=["zip_postal"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MissingField(),
        store_number=sp.MissingField(),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()

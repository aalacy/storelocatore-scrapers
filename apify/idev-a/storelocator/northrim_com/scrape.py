from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("northrim")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-type": "application/x-www-form-urlencoded",
    "Host": "northrim.locatorsearch.com",
    "Origin": "https://northrim.locatorsearch.com",
    "Referer": "https://northrim.locatorsearch.com/index.aspx?s=FCS",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://northrim.com/"
base_url = "https://northrim.locatorsearch.com/GetItems.aspx"
page_url = "https://northrim.com/About-Northrim/Contact-Us/Locations"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=500,
    max_search_results=500,
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
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        logger.info(("Pulling Geo Code %s..." % lat, lng))
        data = {
            "address": "32",
            "lat": str(lat),
            "lng": str(lng),
            "searchby": "FCS|ATMSF|",
            "rnd": "1621588075417",
        }
        locations = bs(
            session.post(base_url, headers=_headers, data=data)
            .text.replace("<![CDATA[", "")
            .replace("]]>", "")
            .replace("<br>", "<br/>")
            .replace("&gt;", ">"),
            "xml",
        ).select("marker")
        total += len(locations)
        for _ in locations:
            addr2 = list(_.select_one("add2").stripped_strings)
            hours = []
            for hh in _.select("div.infowindow table tr")[1:]:
                temp = "".join(hh.stripped_strings)
                if not temp or "Drive-up" in temp or "hour" in temp:
                    break
                hours.append(temp)
            search.found_location_at(
                _["lat"],
                _["lng"],
            )
            store = dict()
            store["lat"] = _["lat"]
            store["lng"] = _["lng"]
            store["name"] = _.select_one(".title").text
            store["street"] = _.select_one("add1").text
            store["city"] = addr2[0].split(",")[0].strip()
            store["state"] = addr2[0].split(",")[1].strip().split(" ")[0].strip()
            store["zip_postal"] = addr2[0].split(",")[1].strip().split(" ")[1].strip()
            store["hours"] = "; ".join(hours) or "<MISSING>"
            store["phone"] = addr2[-1] if _p(addr2[-1]) else "<MISSING>"
            store["type"] = "<MISSING>"
            if "branch" in _["icon"]:
                store["type"] = "branch"
            elif "atm" in _["icon"]:
                store["type"] = "atm"
            yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.ConstantField(page_url),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
            part_of_record_identity=True,
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
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=["phone"],
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(
            mapping=["type"],
        ),
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

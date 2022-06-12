from sgscrape import simple_scraper_pipeline as sp
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord import SgRecord
import re

logger = SgLogSetup().get_logger("ctbcbankusa")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-type": "application/x-www-form-urlencoded",
    "Host": "ctbcbankusav2.locatorsearch.com",
    "Origin": "https://ctbcbankusav2.locatorsearch.com",
    "Referer": "https://ctbcbankusav2.locatorsearch.com/index.aspx?s=FCS",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.ctbcbankusa.com/"
base_url = "https://ctbcbankusav2.locatorsearch.com/GetItems.aspx"

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    expected_search_radius_miles=10,
    use_state=False,
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
            "lat": str(lat),
            "lng": str(lng),
            "searchby": "FCS|",
            "address": "",
            "rnd": "1628009110692",
        }
        locations = bs(
            session.post(base_url, headers=_headers, data=data)
            .text.replace("&gt;", ">")
            .replace("&lt;", "<")
            .replace("<![CDATA[", "")
            .replace("]]]", "")
            .replace("]]>", ""),
            "lxml",
        ).select("marker")
        if locations:
            total += len(locations)
            for _ in locations:

                store = {}
                store["lat"] = _["lat"]
                store["lng"] = _["lng"]
                store["name"] = _.title.text
                store["street"] = _.add1.text
                store["city"] = _.add2.text.split(",")[0]
                addr = list(_.add2.stripped_strings)
                store["state"] = addr[0].split(",")[1].strip().split(" ")[0].strip()
                store["zip_postal"] = (
                    addr[0].split(",")[1].strip().split(" ")[-1].strip()
                )
                store["phone"] = addr[1]
                _hr = _.find("label", string=re.compile(r"^Hours"))
                hours = []
                if _hr:
                    hours = [
                        " ".join(hh.stripped_strings)
                        for hh in _hr.find_next_sibling()
                        .select("table")[0]
                        .select("tr")
                    ]
                store["hours"] = "; ".join(hours) or SgRecord.MISSING
                yield store
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"

        logger.info(f"found: {len(locations)} | total: {total} | progress: {progress}")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(locator_domain),
        page_url=sp.MissingField(),
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
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.ConstantField("branch"),
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

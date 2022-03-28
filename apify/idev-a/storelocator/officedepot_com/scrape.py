from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("officedepot_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

locator_domain = "https://www.officedepot.com/"
base_url = 'https://storelocator.officedepot.com/ajax?&xml_request=<request><appkey>AC2AD3C2-C08F-11E1-8600-DCAD4D48D7F4</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>500</limit><geolocs><geoloc><addressline>'
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def fetch_data(search):
    # Need to add dedupe. Added it in pipeline.
    with SgRequests(verify_ssl=False) as session:
        maxZ = search.items_remaining()
        total = 0
        MAX_DISTANCE = 550
        for zip_code in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Geo Code %s..." % zip_code))
            url = (
                base_url
                + str(zip_code)
                + "</addressline></geoloc></geolocs><searchradius>"
                + str(MAX_DISTANCE)
                + "</searchradius>"
            )
            locations = bs(session.get(url, headers=headers).text, "lxml").find_all(
                "poi"
            )
            total += len(locations)
            for _ in locations:
                search.found_location_at(
                    _.find("latitude").text,
                    _.find("longitude").text,
                )
                hours = []
                for day in days:
                    day = day.lower()
                    if _.find(day):
                        hours.append(f"{day}: {_.find(day).text.strip()}")
                page_url = (
                    "https://www.officedepot.com/storelocator/"
                    + str(_.find("state").text.strip().lower())
                    + "/"
                    + str(_.find("city").text.strip().replace(" ", "-").lower())
                    + "/office-depot-"
                    + str(_.find("clientkey").text.strip())
                    + "/"
                )
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.find("seoid").text.strip(),
                    street_address=_.find("address1").text.strip(),
                    city=_.find("city").text.strip(),
                    state=_.find("state").text.strip(),
                    zip_postal=_.find("postalcode").text.strip(),
                    country_code=_.find("country").text.strip(),
                    phone=_.find("phone").text.strip(),
                    store_number=_.find("clientkey").text.strip(),
                    location_type=_.find("icon").text.strip(),
                    latitude=_.find("latitude").text.strip(),
                    longitude=_.find("longitude").text.strip(),
                    hours_of_operation="; ".join(hours),
                    locator_domain=locator_domain,
                )
            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        search = DynamicZipSearch(
            country_codes=[SearchableCountries.USA],
            expected_search_radius_miles=100,
        )
        results = fetch_data(search)
        for rec in results:
            writer.write_row(rec)

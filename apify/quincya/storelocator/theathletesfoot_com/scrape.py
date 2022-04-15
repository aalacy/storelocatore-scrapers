import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgzip.dynamic import DynamicGeoSearch, Grain_4

logger = SgLogSetup().get_logger("theathletesfoot_com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}
    session = SgRequests()

    locator_domain = "theathletesfoot.com"

    req = session.get(
        "https://theathletesfoot.com/the-athletes-foot-countries/", headers=HEADERS
    )
    base = BeautifulSoup(req.text, "lxml")

    country_dict = {
        "Algeria": "dz",
        "Belgium": "be",
        "Bosnia and Herzegovina": "NA",
        "Croatia": "hr",
        "Denmark": "dk",
        "Ecuador": "ec",
        "France": "fr",
        "Greece": "gr",
        "Indonesia": "id",
        "Italy": "it",
        "Kuwait": "kw",
        "Netherlands": "nl",
        "Mexico": "mx",
        "Peru": "pe",
        "Philippines": "ph",
        "Serbia": "rs",
        "Slovenia": "si",
        "Sweden": "se",
        "Turkey": "tr",
        "USA": "us",
        "Ukraine": "ua",
        "North Macedonia": "mk",
    }
    countries = list(base.find(class_="country-selector__main").stripped_strings)
    for country in countries:
        # Get country coords
        c_code = country_dict[country]

        if c_code == "NA":
            continue

        logger.info(country)

        search = DynamicGeoSearch(
            country_codes=[c_code],
            expected_search_radius_miles=500,
            max_search_distance_miles=500,
            max_search_results=100,
            granularity=Grain_4(),
        )

        for lat, lng in search:
            logger.info(
                "Searching: %s, %s | Items remaining: %s"
                % (lat, lng, search.items_remaining())
            )

            base_link = (
                "https://theathletesfoot.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=100&search_radius=500"
                % (lat, lng)
            )
            req = session.get(base_link, headers=HEADERS)
            base = BeautifulSoup(req.text, "lxml")

            stores = json.loads(base.text)

            for store in stores:
                link = store["permalink"]
                location_name = store["store"]
                country_code = store["country"].replace("usa", "USA")
                if country_code == "USA":
                    street_address = store["address2"]
                    if not street_address:
                        street_address = store["address"]
                else:
                    street_address = (
                        store["address"] + " " + store["address2"]
                    ).strip()
                city = store["city"]
                state = store["state"]
                zip_code = store["zip"]
                if not zip_code:
                    zip_code = "<MISSING>"
                country_code = store["country"].replace("usa", "USA")
                if country_code == "M":
                    country_code = "Mexico"
                store_number = store["id"]
                location_type = "<MISSING>"
                phone = store["phone"].strip()
                if not phone:
                    phone = "<MISSING>"
                hours_of_operation = store["hours"]
                if not hours_of_operation:
                    hours_of_operation = "<MISSING>"
                latitude = store["lat"]
                longitude = store["lng"]
                search.found_location_at(latitude, longitude)

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)

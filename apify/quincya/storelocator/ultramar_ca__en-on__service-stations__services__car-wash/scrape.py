from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_4

log = sglog.SgLogSetup().get_logger(logger_name="ultramar.ca")


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ultramar.ca"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}
    session = SgRequests()

    found = []

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=1000,
        expected_search_radius_miles=500,
        granularity=Grain_4(),
    )
    for lat, lng in search:
        base_link = (
            "https://www.ultramar.ca/en-on/find-services-stations/ajax-update-store-list/?latitude=%s&longitude=%s&is_ultralave=on"
            % (lat, lng)
        )
        html = session.get(base_link, headers=headers).json()["html"]
        base = BeautifulSoup(html, "lxml")

        stores = base.find_all(class_="localization__right-col-item")
        for store in stores:

            street_address = store["data-address"]
            country_code = "CA"
            store_number = store["data-id"]
            latitude = store["data-lat"]
            longitude = store["data-lng"]
            search.found_location_at(float(latitude), float(longitude))

            link = locator_domain + store["data-details_url"].split("?c=")[0]
            if link in found:
                continue
            found.append(link)
            log.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name = base.h1.text
            phone = base.find(itemprop="telephone").text
            city = base.find(itemprop="addressLocality").text
            state = base.find(itemprop="addressRegion").text
            zip_code = base.find(itemprop="postalCode").text
            location_type = ", ".join(
                list(base.find(class_="station__icons-list").stripped_strings)
            )
            hours_of_operation = " ".join(
                list(base.find_all(class_="station__icon-text")[-1].stripped_strings)
            )

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

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="nfumutual.co.uk")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "https://www.nfumutual.co.uk"

    max_distance = 25

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_search_distance_miles=max_distance,
        max_search_results=None,
    )

    log.info("Running sgzips..")

    for postcode in search:
        base_link = (
            "https://www.nfumutual.co.uk/Postcode/RadiusFind?productTag=All+Products&address="
            + postcode
        )
        stores = session.get(base_link, headers=headers).json()["branches"]

        for store in stores:
            location_name = store["name"]
            hours_of_operation = (
                BeautifulSoup(store["openinghours"], "lxml")
                .p.text.split("Call")[0]
                .replace("Visit us:", "")
                .strip()
            )
            if hours_of_operation.lower() == "closed":
                continue

            raw_address = store["address"]
            addr = parse_address_intl(raw_address)
            try:
                street_address = addr.street_address_1 + " " + addr.street_address_2
            except:
                street_address = addr.street_address_1
            if street_address:
                if len(street_address) < 3:
                    street_address = raw_address
            else:
                street_address = raw_address
            city = addr.city
            state = addr.state
            zip_code = store["postcode"].split("(")[0].strip()
            if zip_code and street_address:
                if zip_code.lower() in street_address.lower():
                    zip_loc = street_address.lower().find(zip_code.lower())
                    street_address = street_address[:zip_loc].strip()
            if not street_address:
                street_address = " ".join(raw_address.split(",")[:-2])
                if city:
                    street_address = street_address.replace(city, "").strip()
            if not city:
                if "Melrose" in street_address:
                    city = "Melrose"
                if "Westray" in street_address:
                    city = ""
                else:
                    city = raw_address.split(",")[-2].strip()
                if city in street_address:
                    street_address = street_address[
                        : street_address.rfind(city)
                    ].strip()
            if street_address[-1] == ",":
                street_address = street_address[:-1]
            country_code = "UK"
            store_number = store["id"]
            phone = store["telephone"]
            latitude = store["lat"]
            longitude = store["lng"]
            location_type = ""
            search.found_location_at(float(latitude), float(longitude))
            link = locator_domain + store["url"]

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
                    raw_address=raw_address,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)

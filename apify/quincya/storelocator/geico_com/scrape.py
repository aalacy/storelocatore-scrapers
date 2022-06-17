from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }
    locator_domain = "geico.com"

    max_distance = 50

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        expected_search_radius_miles=max_distance,
    )

    for postcode in search:

        base_link = (
            "https://www.geico.com/public/php/geo_map.php?address=%s&language=en&type=Sales&captcha=false"
            % postcode
        )

        try:
            res_json = session.get(base_link, headers=headers).json()[1:]
            if not res_json:
                search.found_nothing()
                continue
        except:
            search.found_nothing()
            continue

        for loc in res_json:

            location_name = loc["displayName"].strip()
            phone_number = loc["contactPhone"]
            if not phone_number:
                phone_number = "<MISSING>"
            page_url = "https://www.geico.com" + loc["url"]
            lat = loc["latitude"]
            longit = loc["longitude"]
            search.found_location_at(lat, longit)

            raw_address = loc["formattedAddress"]
            city = loc["city"]
            state = raw_address.split(",")[-1].split()[0].strip()
            zip_code = raw_address.split(",")[-1].split()[-1].strip()
            street_address = raw_address[: raw_address.rfind(city) :].strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()
            country_code = "US"
            store_number = loc["soa"]
            location_type = "<MISSING>"
            hours = BeautifulSoup(loc["locationHours"], "lxml").get_text(" ")
            if "day" not in hours.lower():
                req = session.get(page_url, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                hours = " ".join(
                    list(base.find_all(class_="box gfr_margin")[1].stripped_strings)[1:]
                )
                if "day" not in hours.lower():
                    hours = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone_number,
                    location_type=location_type,
                    latitude=lat,
                    longitude=longit,
                    hours_of_operation=hours,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)

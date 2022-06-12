from bs4 import BeautifulSoup

from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    max_results = 25
    max_distance = 50

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    with SgRequests() as session:
        for lat, lng in search:
            r = session.get(
                "https://www.bonsecours.com/bonsecours/api/v1/locations?Latitude="
                + str(lat)
                + "&Longitude="
                + str(lng),
                headers=headers,
            ).json()
            for link in r["Results"]:
                location_type = link["Location"]["FacilityType"]["SchemaPlaceType"]
                page_url = (
                    "https://www.bonsecours.com" + link["Location"]["DetailsLink"]
                )
                location_name = link["Location"]["Name"]
                street_address = link["Location"]["Address"]["StreetDisplay"]
                city = link["Location"]["Address"]["City"].replace(",", "").strip()
                state = link["Location"]["Address"]["StateAbbr"]
                zipp = (
                    link["Location"]["Address"]["PostalCode"].replace(".", "").strip()
                )
                country_code = "US"
                store_number = "<MISSING>"
                r1 = session.get(page_url, headers=headers)
                soup_loc = BeautifulSoup(r1.text, "lxml")
                phone = link["Location"]["Phone"]
                try:
                    hours_of_operation = " ".join(
                        list(
                            soup_loc.find(
                                "div",
                                class_="col w-100 w-sm-50 w-md-100 w-xl-50 py3 small bl",
                            ).stripped_strings
                        )
                    )
                except:
                    hours_of_operation = "<MISSING>"
                latitude = link["Location"]["Latitude"]
                longitude = link["Location"]["Longitude"]
                search.found_location_at(latitude, longitude)

                street_address = (
                    street_address.split("Floor")[0]
                    .split("Suite")[0]
                    .replace(",", "")
                    .replace(state, "")
                )
                if street_address.strip()[0] == "0":
                    street_address = street_address.strip()[1:]

                yield SgRecord(
                    locator_domain="https://www.bonsecours.com/",
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipp,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                    page_url=page_url,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            record_id=SgRecordID(
                {SgRecord.Headers.LOCATION_TYPE, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)


if __name__ == "__main__":
    scrape()

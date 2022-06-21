from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.chopard.com"
    for country in SearchableCountries.ALL:

        search = DynamicGeoSearch(
            country_codes=[f"{country}"],
            max_search_distance_miles=100,
            expected_search_radius_miles=100,
            max_search_results=None,
        )
        for lat, long in search:

            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.chopard.com",
                "Connection": "keep-alive",
                "Referer": "https://www.chopard.com/en-intl/store-locator.html",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }

            data = {
                "lat": f"{str(lat)}",
                "lng": f"{str(long)}",
                "zoom": "8",
            }

            r = session.post(
                "https://www.chopard.com/on/demandware.store/Sites-chopard-Site/en/Stores-Reposition",
                headers=headers,
                data=data,
            )
            jss = r.json()["stores"]
            try:
                js = eval(jss)
            except:
                search.found_nothing()
                continue
            search.found_location_at(lat, long)
            for j in js:

                page_url = "https://www.chopard.com/en-intl/store-locator.html"
                location_name = j.get("name") or "<MISSING>"
                location_type = j.get("type") or "<MISSING>"
                street_address = j.get("address") or "<MISSING>"
                state = "<MISSING>"
                postal = j.get("zip") or "<MISSING>"
                country_code = j.get("country") or "<MISSING>"
                city = j.get("city") or "<MISSING>"
                latitude = j.get("position").get("lat")
                longitude = j.get("position").get("lng")

                phone = j.get("phone") or "<MISSING>"
                hours_of_operation = j.get("openings") or "<MISSING>"
                hours_of_operation = (
                    str(hours_of_operation).replace("<br>", " ").strip()
                )

                row = SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=postal,
                    country_code=country_code,
                    store_number=SgRecord.MISSING,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.LATITUDE,
                }
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)

import httpx
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.pause_resume import CrawlStateSingleton
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries, Grain_1_KM
from concurrent import futures
from sglogging import sglog

locator_domain = "https://ashleyfurniture.com/"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    api_url = f"https://stores.ashleyfurniture.com/umbraco/surface/locate/GetDataByCoordinates?longitude={long}&latitude={lat}&distance=50000&units=miles&amenities=&paymentMethods="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    try:
        r = SgRequests.raise_on_err(session.post(api_url, headers=headers))
        log.info(f"## Response: {r}")
        assert isinstance(r, httpx.Response)
        assert 200 == r.status_code
        js = r.json()["StoreLocations"]

        for j in js:
            store_number = j.get("LocationNumber")
            page_url = "https://stores.ashleyfurniture.com/"
            location_name = j.get("Name") or "<MISSING>"
            street_address = j.get("Address") or "<MISSING>"
            city = j.get("ExtraData").get("Address").get("Locality") or "<MISSING>"
            state = j.get("ExtraData").get("Address").get("Region") or "<MISSING>"
            postal = j.get("ExtraData").get("Address").get("PostalCode") or "<MISSING>"
            country_code = "".join(j.get("ExtraData").get("Address").get("CountryCode"))
            city_slug = city.replace(" ", "-").lower()
            state_slug = state.replace(" ", "-").lower()
            if country_code == "US":
                page_url = f"https://stores.ashleyfurniture.com/store/us/{state_slug}/{city_slug}/{store_number}/"
            if country_code == "CA":
                page_url = f"https://stores.ashleyfurniture.com/store/ca/{state_slug}/{city_slug}/{store_number}/"
            phone = j.get("ExtraData").get("Phone") or "<MISSING>"
            latitude = j.get("Location").get("coordinates")[1] or "<MISSING>"
            longitude = j.get("Location").get("coordinates")[0] or "<MISSING>"

            hours_of_operation = ""
            try:
                raw_hours = j["ExtraData"]["HoursOfOpStruct"]
                for day in raw_hours:
                    if day == "SpecialHours":
                        continue

                    try:
                        day_hours = (
                            raw_hours[day]["Ranges"][0]["StartTime"]
                            + "-"
                            + raw_hours[day]["Ranges"][0]["EndTime"]
                        )
                    except:
                        day_hours = "Closed"

                    hours_of_operation = (
                        hours_of_operation + " " + day + " " + day_hours
                    ).strip()
            except:
                try:
                    hours_of_operation = ""
                    days = ["Su ", "Mo ", "Tu ", "We ", "Th ", "Fr ", "Sa "]
                    raw_hours = j["ExtraData"]["CustomerServiceHours"].split(",")
                    for i, day in enumerate(days):
                        hours_of_operation = (
                            hours_of_operation + " " + day + raw_hours[i]
                        ).strip()
                except:
                    hours_of_operation = "<MISSING>"

            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)
    except Exception as e:
        log.info(f"Err at #L100: {e}")


def fetch_data(sgw: SgWriter):

    for country in SearchableCountries.ALL:
        country = str(country).lower()
        if country != "us":
            continue
        coords = DynamicGeoSearch(
            country_codes=[f"{country}"],
            max_search_distance_miles=5,
            expected_search_radius_miles=5,
            max_search_results=None,
            granularity=Grain_1_KM(),
        )

        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    CrawlStateSingleton.get_instance().save(override=True)
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)

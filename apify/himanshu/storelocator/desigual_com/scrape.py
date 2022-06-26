from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.desigual.com/"
    api_url = f"https://www.desigual.com/on/demandware.store/Sites-dsglcom_prod_globale_north-Site/en_US/Address-SearchStoreAddress?longitude={str(long)}&latitude={str(lat)}&deliveryPoint=STORE&radius=700&showOfficialStores=false&showOutlets=false&showAuthorized=false&showOnlyAllowDevosStores=false"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)
    try:
        js = r.json()["shippingAddresses"]
    except:
        return
    for j in js:

        page_url = j.get("detailUrl") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        hours_list = []
        hours = j["schedule"]
        if hours:
            for hour in hours:
                day = hour["name"]
                if hour["isOpen"] is True:
                    time = hour["value"]
                else:
                    time = "Closed"
                hours_list.append(day + ":" + time)

        hours_of_operation = "; ".join(hours_list).strip()

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


def fetch_data(sgw: SgWriter):

    for country in SearchableCountries.ALL:
        coords = DynamicGeoSearch(
            country_codes=[f"{country}"],
            max_search_distance_miles=250,
            expected_search_radius_miles=70,
            max_search_results=None,
        )

        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL}), duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)

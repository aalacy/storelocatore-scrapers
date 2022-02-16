from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.canadiantire.ca/"
    ttypes = [
        "store",
        "pitStop",
        "propanefill,propaneswap,cylinderfne,cylinderex",
        "gas",
        "diesel",
        "carwash",
    ]
    for t in ttypes:
        api_url = f"https://api-triangle.canadiantire.ca/dss/services/v5/stores?lang=en&radius=9999&maxCount=9999&lat={lat}&lng={long}&storeType={t}&includeServicesData=true"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        }

        session = SgRequests()

        r = session.get(api_url, headers=headers)
        try:
            js = r.json()
        except:
            return
        for j in js:

            location_name = j.get("storeName")
            street_address = (
                f"{j.get('storeAddress1')} {j.get('storeAddress2')}".strip()
            )
            city = j.get("storeCityName")
            state = j.get("storeProvince")
            postal = j.get("storePostalCode")
            country_code = "CA"
            phone = j.get("storeTelephone")
            latitude = j.get("storeLatitude")
            location_type = "<MISSING>"
            services = j.get("services") or "<MISSING>"
            type_tmp = []
            if services != "<MISSING>":
                for s in services:
                    types = s.get("serviceName")
                    type_tmp.append(types)
                location_type = ", ".join(type_tmp)
            longitude = j.get("storeLongitude")
            store_number = j.get("storeNumber")
            page_url = f"https://www.canadiantire.ca/en/store-details/{str(state).lower()}/{j.get('storeCrxNodeName')}.store.html"
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            tmp = []
            for d in days:
                day = d
                try:
                    opens = j.get("workingHours").get("general").get(f"{d}OpenTime")
                    closes = j.get("workingHours").get("general").get(f"{d}CloseTime")
                    line = f"{day} {opens} - {closes}"
                except:
                    line = f"{day} Closed"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp) or "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_search_distance_miles=200,
        expected_search_radius_miles=200,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

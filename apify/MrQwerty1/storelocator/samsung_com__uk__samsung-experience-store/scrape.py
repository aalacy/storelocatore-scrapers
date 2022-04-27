from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    x = SearchableCountries

    countries = [
        x.UNITED_ARAB_EMIRATES,
        x.AUSTRIA,
        x.AUSTRALIA,
        x.SWITZERLAND,
        x.DENMARK,
        x.FINLAND,
        x.FRANCE,
        x.HUNGARY,
        x.NORWAY,
        x.NEW_ZEALAND,
        x.RUSSIA,
        x.SWEDEN,
        x.SINGAPORE,
        x.THAILAND,
        x.BRITAIN,
        x.VIET_NAM,
    ]

    search = DynamicGeoSearch(country_codes=countries, expected_search_radius_miles=100)
    for lat, lng in search:
        cc = search.current_country().lower()
        locator_domain = f"https://samsung.com/{cc}/samsung-experience-store/"
        page_url = f"https://www.samsung.com/{cc}/samsung-experience-store/locations/"

        part = f'{{"latitude":"{lat}", "longitude":"{lng}"}}'
        data = (
            '{"countryCode":"'
            + cc.upper()
            + '","geoCenterArea":{"center":'
            + part
            + ',"distance":500000},"filters":[{"columnName":"storeTypes","operation":"equal","value":["1_ses"]}]}'
        )
        r = session.post(api, data=data, headers=headers)
        if r.status_code == 503:
            continue
        js = r.json()["locations"]

        for j in js:
            types = j.get("storeTypes")
            if "1_ses" not in types:
                continue

            location_type = "Samsung Experience Store"
            store_number = j.get("searchableId")
            location_name = j.get("name")
            a = j.get("address") or {}
            street_address = a.get("street")
            city = j.get("locality")
            postal = a.get("zip")
            phone = j.get("telephone")
            c = j.get("coordinates") or {}
            latitude = c.get("latitude")
            longitude = c.get("longitude")
            hours_of_operation = j.get("openingHours")

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                zip_postal=postal,
                country_code=cc,
                latitude=latitude,
                longitude=longitude,
                store_number=store_number,
                location_type=location_type,
                phone=phone,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    api = "https://papi.gethatch.com/locations/5c88b7e546e0fb000143fc7c/geo/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://www.samsung.com/",
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Origin": "*",
        "Origin": "https://www.samsung.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "TE": "trailers",
        "Pragma": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

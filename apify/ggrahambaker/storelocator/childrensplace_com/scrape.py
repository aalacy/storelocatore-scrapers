import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.childrensplace.com/"
    api_url = (
        "https://www.childrensplace.com/api/v2/store/findStoresbyLatitudeandLongitude"
    )

    headers = {
        "authority": "www.childrensplace.com",
        "method": "GET",
        "path": "/api/v2/store/findStoresbyLatitudeandLongitude",
        "scheme": "https",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-store, must-revalidate",
        "referer": "https://www.childrensplace.com/us/store-locator",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
        "pragma": "no-cache",
        "expires": "0",
        "devictype": "desktop",
        "langid": "-1",
        "storeid": "10151",
        "catalogid": "10551",
        "latitude": str(lat),
        "longitude": str(long),
        "maxitems": "1000",
        "radius": "500",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()["PhysicalStore"][0]

    for j in js:

        latitude = j["latitude"]
        longitude = j["longitude"]
        street_address = j["addressLine"]["0"] + " " + j["addressLine"]["1"]
        city = j["city"].strip()
        state = j["stateOrProvinceName"].strip()
        postal = j["postalCode"].strip()
        country_code = j["country"].strip()
        phone = j["telephone1"].strip()
        store_number = j["uniqueId"]
        location_name = j["description"]["displayStoreName"]
        hours_of_operation = "<MISSING>"
        hours_obj = json.loads(j["attribute"]["displayValue"])["storehours"]
        tmp = []
        if hours_obj:
            for h in hours_obj:
                day = h.get("nick")
                opens = str(h.get("availability")[0].get("from"))
                if opens.find("T") != -1:
                    opens = (
                        opens.split("T")[1]
                        .replace(":00:00", ":00")
                        .replace(":30:00", ":30")
                        .strip()
                    )
                closes = str(h.get("availability")[0].get("to"))
                if closes.find("T") != -1:
                    closes = (
                        closes.split("T")[1]
                        .replace(":00:00", ":00")
                        .replace(":30:00", ":30")
                        .strip()
                    )
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        page_url = (
            "https://www.childrensplace.com/us/store/"
            + location_name.replace(" ", "")
            + "-"
            + state
            + "-"
            + city.replace(" ", "")
            + "-"
            + postal.replace(" ", "")
            + "-"
            + store_number
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
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
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

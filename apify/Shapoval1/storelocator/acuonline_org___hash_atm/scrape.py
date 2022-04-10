import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch, Grain_2
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from concurrent import futures
from sglogging import sglog


locator_domain = "acuonline.org"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def get_data(coord, sgw: SgWriter):
    lat, lng = coord

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://03919locator.wave2.io",
        "Connection": "keep-alive",
        "Referer": "https://03919locator.wave2.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }

    data = {
        "Latitude": f"{lat}",
        "Longitude": f"{lng}",
        "Address": "",
        "City": "",
        "State": "",
        "Zipcode": "",
        "Country": "",
        "Action": "textsearch",
        "ActionOverwrite": "",
        "Filters": "FCS,FIITM,FIATM,ATMSF,ATMDP,ESC,",
    }

    session = SgRequests()

    r = session.post(
        "https://locationapi.wave2.io/api/client/getlocations",
        headers=headers,
        data=json.dumps(data),
    )
    log.info(f"From {lat,lng} :: Response: {r.status_code}")
    try:
        js = r.json()["Features"]

        if js:
            log.info(f"From {lat,lng} stores = {len(js)}")
            for j in js:
                a = j.get("Properties")
                page_url = "https://www.acuonline.org/home/resources/locations"
                street_address = "".join(a.get("Address")).capitalize() or "<MISSING>"
                city = a.get("City") or "<MISSING>"
                state = a.get("State") or "<MISSING>"
                postal = a.get("Postalcode") or "<MISSING>"
                country_code = a.get("Country") or "<MISSING>"
                phone = a.get("Phone") or "<MISSING>"
                latitude = a.get("Latitude") or "<MISSING>"
                store_number = a.get("LocationId") or "<MISSING>"
                longitude = a.get("Longitude") or "<MISSING>"
                location_type = j.get("LocationFeatures").get("LocationType")
                location_name = a.get("LocationName")
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                tmp = []
                for d in days:
                    day = d
                    try:
                        opens = a.get(f"{d}Open")
                        closes = a.get(f"{d}Close")
                        line = f"{day} {opens} - {closes}"
                        if opens == closes:
                            line = "<MISSING>"
                    except:
                        line = "<MISSING>"
                    tmp.append(line)
                hours_of_operation = "; ".join(tmp)
                if hours_of_operation.count("<MISSING>") == 7:
                    hours_of_operation = "<MISSING>"
                hours_of_operation = hours_of_operation.replace(
                    "Closed -", "Closed"
                ).strip()
                if hours_of_operation.count("Closed") == 7:
                    hours_of_operation = "Closed"
                if hours_of_operation.find("<MISSING>") != -1:
                    hours_of_operation = "<MISSING>"
                coord.found_location_at(float(latitude), float(longitude))
                row = SgRecord(
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
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )

                sgw.write_row(row)
    except Exception as e:
        log.info(f"No JSON: {e}")
        pass


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=0.5,
        max_search_results=100,
        granularity=Grain_2(),
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)

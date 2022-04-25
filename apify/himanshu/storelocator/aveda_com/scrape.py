from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://aveda.com/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.aveda.com/locations",
        "X-CSRF-Token": "fe8fd28ef68ed90b8ed305f6a03981e6004a0178,14956ec50d45e89f24c040fd3b0e4a35f1bc9f25,1647896777",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.aveda.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "dbgmethod": "locator.doorsandevents",
    }

    data = (
        "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A7%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+SALON_ID%2C+ACTUAL_DOORNAME%2C+ACTUAL_ADDRESS%2C+ACTUAL_ADDRESS2%2C+ACTUAL_CITY%2C+STORE_TYPE%2C+STATE%2C+ZIP%2C+DOORNAME%2C+ADDRESS%2C+ADDRESS2%2C+CITY%2C+STATE_OR_PROVINCE%2C+ZIP_OR_POSTAL%2C+COUNTRY%2C+PHONE1%2C+CLASSIFICATION%2C+IS_SALON%2C+IS_LIFESTYLE_SALON%2C+IS_INSTITUTE%2C+IS_FAMILY_SALON%2C+IS_CONCEPT_SALON%2C+IS_STORE%2C+HAS_EXCLUSIVE_HAIR_COLOR%2C+HAS_PURE_PRIVILEGE%2C+HAS_PERSONAL_BLENDS%2C+HAS_GIFT_CARDS%2C+HAS_PAGE%2C+HAS_SPA_SERVICES%2C+IS_GREEN_SALON%2C+HAS_RITUALS%2C+DO_NOT_REFER%2C+HAS_EVENTS%2C+LONGITUDE%2C+LATITUDE%2C+LOCATION%2C+WEBURL%2C+EMAILADDRESS%2C+APPT_URL%22%2C%22radius%22%3A%22100%22%2C%22country%22%3A%22USA%22%2C%22city%22%3A%22USA%22%2C%22region_id%22%3A%220%22%2C%22language_id%22%3A%22%22%2C%22latitude%22%3A"
        + str(lat)
        + "%2C%22longitude%22%3A"
        + str(long)
        + "%2C%22uom%22%3A%22miles%22%2C%22primary_filter%22%3A%22filter_salon_spa_store%22%2C%22filter_HC%22%3A0%2C%22filter_PP%22%3A0%2C%22filter_SS%22%3A0%2C%22filter_SR%22%3A0%2C%22filter_EM%22%3A0%7D%5D%7D%5D"
    )
    r = session.post(
        "https://www.aveda.com/rpc/jsonrpc.tmpl",
        headers=headers,
        params=params,
        data=data,
    )

    try:
        js = r.json()[0]["result"]["value"]["results"]
    except TypeError:
        return

    for j in js.values():

        store_number = j.get("DOOR_ID")
        page_url = (
            f"https://www.aveda.com/locator/get_the_facts.tmpl?DOOR_ID={store_number}"
        )
        location_name = j.get("ACTUAL_DOORNAME") or "<MISSING>"
        street_address = j.get("ACTUAL_ADDRESS") or "<MISSING>"
        street_address = str(street_address).replace(",", "").strip()
        city = j.get("ACTUAL_CITY") or "<MISSING>"
        state = j.get("STATE") or "<MISSING>"
        if str(state).isdigit():
            state = "<MISSING>"
        postal = j.get("ZIP") or "<MISSING>"
        if postal == "0" or postal == "0000" or postal == ".":
            postal = "<MISSING>"
        country_code = j.get("COUNTRY") or "<MISSING>"
        phone = j.get("PHONE1") or "<MISSING>"
        if phone == "-":
            phone = "<MISSING>"
        if str(postal).find("N/A") != -1:
            postal = "<MISSING>"
        latitude = j.get("LATITUDE") or "<MISSING>"
        longitude = j.get("LONGITUDE") or "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"
        location_type = j.get("CLASSIFICATION") or "<MISSING>"

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
    for country_code in SearchableCountries.ALL:
        coords = DynamicGeoSearch(
            country_codes=[f"{country_code}"],
            max_search_distance_miles=100,
            expected_search_radius_miles=100,
            max_search_results=None,
        )

        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)

from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api_url = "https://marketsquareonline.com/ajax/index.php"
    data = '-----------------------------370899683133672295103336163816\r\nContent-Disposition: form-data; name="method"\r\n\r\nPOST\r\n-----------------------------370899683133672295103336163816\r\nContent-Disposition: form-data; name="apiurl"\r\n\r\nhttps://marketsquare.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1\r\n-----------------------------370899683133672295103336163816--\r\n'

    r = session.post(api_url, data=data, headers=headers)
    js = r.json()["GetClientStores"]

    for j in js:
        street_address = j.get("AddressLine1")
        city = j.get("City")
        state = j.get("StateName")
        postal = j.get("ZipCode")
        country_code = "US"
        store_number = j.get("StoreNumber")
        location_name = j.get("ClientStoreName")
        phone = j.get("StorePhoneNumber")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        hours_of_operation = j.get("StoreTimings") or ""
        hours_of_operation = hours_of_operation.replace("pm ", "pm;")

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://marketsquareonline.com/"
    page_url = "https://marketsquareonline.com/contact"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "multipart/form-data; boundary=---------------------------370899683133672295103336163816",
        "Origin": "https://marketsquareonline.com",
        "Connection": "keep-alive",
        "Referer": "https://marketsquareonline.com/contact",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)

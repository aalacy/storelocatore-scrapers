from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address, International_Parser
from sglogging import sglog


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    postal = adr.postcode

    return street_address, postal


def fetch_data(sgw: SgWriter):
    api = "https://sea.sunglasshut.com/api/content/render/false/limit/9999/type/json/query/+contentType:SghStoreLocator%20+languageId:9%20+deleted:false%20+working:true/orderby/modDate%20desc"

    headers = {
        "Referer": "https://www.sunglasshut.com/de/sunglasses/store-locations/map?",
        "Cookie": "WC_USERACTIVITY_-1002=-1002%2C14351%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C1383781219%2CWTtx63G9jGWIMiFo8zvyj0s_sq=lux-sgh-prod%3D%2526c.%2526a.%2526activitymap.%2526page%253D%25252Fde%25252Fsunglasses%25252Fstore-locations%2526link%253DSuchen%2526region%253DBODY%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253D%25252Fde%25252Fsunglasses%25252Fstore-locations%2526pidt%253D1%2526oid%253DSuchen%2526oidt%253D3%2526ot%253DSUBMIT; dtSa=true%7CU%7C-1%7CSuchen%7C-%7C1634204053743%7C404011276_203%7Chttps%3A%2F%2Fwww.sunglasshut.com%2Fde%2Fsunglasses%2Fstore-locations%7CStore%20Locator%7C1634204035154%7C%7C",
    }

    r = session.get(api, headers=headers)
    logger.info(f"Response: {r}")
    js = r.json()["contentlets"]
    logger.info(f"Total Count: {len(js)}")
    for j in js:
        location_name = j.get("name")
        slug = j.get("URL_MAP_FOR_CONTENT") or "/"
        slug = slug.replace("-details", "")
        page_url = f"https://sea.sunglasshut.com/sg{slug}"
        store_number = j.get("identifier")
        raw_address = j.get("address") or ""
        street_address, postal = get_international(raw_address)
        if len(street_address) < 5:
            street_address = raw_address.split(",")[0].strip()
        city = j.get("city")
        country_code = j.get("state")
        phone = j.get("phone")
        latitude = j.get("geographicCoordinatesLatitude")
        longitude = j.get("geographicCoordinatesLongitude")
        if latitude == 0:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            _tmp.append(f"{day}: {j.get(day)}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            location_name=location_name,
            page_url=page_url,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "sea.sunglasshut.com"
    logger = sglog.SgLogSetup().get_logger(logger_name=locator_domain)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

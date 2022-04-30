import re
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sglogging import sglog


def get_ids():
    r = session.get("https://www.melia.com/rest/hotels/destinations-tree?lang=en")

    return re.findall(r'"hotelCode":"(.*?)"', r.text)


def get_data(store_number, sgw: SgWriter):
    api = f"https://www.melia.com/rest/hotels/hotel-sheet/{store_number}/en"
    r = session.get(api)
    if r.status_code != 200:
        logger.info(f"{api}: {r.status_code}")
        return

    j = r.json()["hotel"]["hotelSection"]
    location_name = j.get("title")
    street_address = j.get("address") or ""
    street_address = " ".join(street_address.split())
    city = j.get("location")
    postal = j.get("postalCode")
    country_code = j.get("countryCode")
    phone = j.get("phoneContact")
    latitude = j.get("latitudeCoordinates")
    longitude = j.get("longitudeCoordinates")
    slug = j.get("url")
    page_url = f"https://www.melia.com{slug}"

    location_type = SgRecord.MISSING
    cats = j.get("categories") or []
    for c in cats:
        if c.get("type") == "Marca":
            location_type = c.get("title")
            break

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        location_type=location_type,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.melia.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="melia")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

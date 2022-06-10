from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    ids = set()
    api = "https://ecgplacesmw.colruytgroup.com/ecgplacesmw/v3/fr/places/searchPlaces?ensignId=13&placeTypeId=1"
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        _id = j.get("branchId")
        ids.add(_id)

    return ids


def get_data(store_number, sgw: SgWriter):
    api = f"https://ecgplacesmw.colruytgroup.com/ecgplacesmw/v3/fr/places/getByBranchIdAndPlaceType?branchId={store_number}&placeTypeId=1"
    r = session.get(api, headers=headers)
    j = r.json()

    location_name = j.get("branchName")
    a = j.get("address") or {}
    name = a.get("streetName") or ""
    number = a.get("houseNumber") or ""
    street_address = f"{name} {number}".replace("-", "").strip()
    city = a.get("cityName") or ""
    postal = a.get("postalcode")
    country_code = "BE"
    try:
        phone = j["telephones"][0]["number"].replace("..", "")
    except:
        phone = SgRecord.MISSING

    page_url = f"https://www.dreamland.be/e/fr/dl/magasin?storedetails={store_number}"
    g = j.get("geoCoordinates") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    _tmp = []
    try:
        hours = j["placeOpeningHours"]["openinghoursList"]
    except:
        hours = []

    days = []
    for h in hours:
        day = h.get("dayName")
        if day in days:
            continue

        days.append(day)
        inters = []
        times = h.get("consolidatedOpeningHours") or []
        for t in times:
            start = str(t.get("openHour")).zfill(4)
            end = str(t.get("closeHour")).zfill(4)
            inter = f"{start[:2]}:{start[2:]}-{end[:2]}:{end[2:]}"
            inters.append(inter)

        if inters:
            _tmp.append(f'{day}: {"|".join(inters)}')
        else:
            _tmp.append(f"{day}: Gesloten")

    hours_of_operation = ";".join(_tmp) or "Gesloten"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.dreamland.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    ids = set()
    data = {
        "ShopLocator_InputParams[dmlLat]": "52,52",
        "ShopLocator_InputParams[dmlLng]": "13,40",
        "ShopLocator_InputParams[intRadius]": "5000",
    }
    r = session.post(
        "https://jannys-eis.com/Data/ShopLocator", headers=headers, data=data
    )
    js = r.json()
    for j in js:
        ids.add(j.get("shopID"))

    return ids


def get_data(store_number, sgw: SgWriter):
    data = {"ID": str(store_number)}
    api = "https://jannys-eis.com/Data/ShopsSelectShopLocatorDetails"
    r = session.post(api, headers=headers, data=data)
    j = r.json()

    location_name = j.get("shopName")
    street_address = j.get("street")
    city = j.get("city") or ""
    if "(" in city:
        city = city.split("(")[0].strip()

    postal = j.get("postCode")
    country_code = "DE"
    phone = j.get("primary_Phone")
    latitude = j.get("googleX")
    longitude = j.get("googleY")
    slug = j.get("ufurl")
    page_url = f"https://{slug}.jannys.de"

    if j.get("preorderActive") and not j.get("lieferServiceActive"):
        location_type = "Mit Abholservice"
    elif j.get("preorderActive") and j.get("lieferServiceActive"):
        location_type = "Mit Abhol- und Lieferservice"
    else:
        location_type = "Janny's Shop"

    _tmp = []
    days = ["mo", "tu", "we", "th", "fr", "sa", "su"]
    for day in days:
        start = j.get(f"{day}O") or ""
        if start:
            start = start.split("T")[-1].rsplit(":00", 1)[0]

        end = j.get(f"{day}C") or ""
        if end:
            end = end.split("T")[-1].rsplit(":00", 1)[0]

        if start and end:
            _tmp.append(f"{day.upper()}: {start}-{end}")
        else:
            _tmp.append(f"{day.upper()}: Closed")

    hours_of_operation = ";".join(_tmp)

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
        location_type=location_type,
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
    locator_domain = "https://jannys-eis.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Referer": "https://jannys-eis.com/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jannys-eis.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

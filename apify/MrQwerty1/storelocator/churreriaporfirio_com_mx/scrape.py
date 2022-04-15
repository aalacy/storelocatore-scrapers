import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    clicks = tree.xpath("//a[contains(@onclick, 'sucursales(')]/@onclick")
    for c in clicks:
        _id = c.split("(")[-1].replace(")", "")
        api = f"https://www.churreriaporfirio.com.mx/api/getSucursalById/{_id}"
        urls.add(api)

    latams = tree.xpath("//a[contains(@onclick, 'sucursalesLatam(')]/@onclick")
    for la in latams:
        _id = la.split("(")[-1].replace(")", "")
        api = f"https://www.churreriaporfirio.com.mx/api/getSucursalLatamById/{_id}"
        urls.add(api)

    return urls


def get_data(api, sgw: SgWriter):
    store_number = api.split("/")[-1]
    r = session.get(api, headers=headers)
    source = r.json()["data"]
    j = json.loads(source)

    location_name = j.get("name")
    adr1 = j.get("calle") or ""
    adr2 = j.get("numero_exterior") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = j.get("ciudad")
    state = j.get("mexico_states_name")
    postal = j.get("codigo_postal")
    country_code = "MX"
    phone = j.get("telefono") or ""
    if "/" in phone:
        phone = phone.split("/")[0].strip()
    if phone:
        if phone[0].isalpha() and phone[-1].isalpha():
            phone = SgRecord.MISSING
        if phone[0].isdigit() and phone[-1].isalpha():
            _tmp = []
            for p in phone:
                if p.isdigit():
                    _tmp.append(p)
            phone = "".join(_tmp)
    latitude = j.get("latitud")
    longitude = j.get("longitud")

    hours = j.get("openingHours") or []
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
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
    apis = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, api, sgw): api for api in apis}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.churreriaporfirio.com.mx/"
    page_url = "https://www.churreriaporfirio.com.mx/sucursales"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

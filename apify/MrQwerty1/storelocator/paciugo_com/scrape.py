from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_param():
    coords = dict()
    ids = []

    r = session.get(
        "https://paciugo.com/wp-content/themes/paciugo/inc/store-locator/phpsqlsearch_genxml.php",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker")
    for m in markers:
        _id = "".join(m.xpath("./@storeid"))
        lat = "".join(m.xpath("./@lat")) or SgRecord.MISSING
        lng = "".join(m.xpath("./@lng")) or SgRecord.MISSING
        coords[_id] = (lat, lng)
        ids.append(_id)

    return coords, ids


def get_data(store_number, sgw: SgWriter):
    data = {"action": "ajaxretrievestorebyid", "storeID": store_number}
    r = session.post(api, data=data, headers=headers)
    tree = html.fromstring(r.json()["message"].replace("\u201d", ""))
    location_name = "".join(tree.xpath("//h3[@itemprop='name']/text()")).strip()
    if "coming soon" in location_name.lower():
        return
    adr1 = "".join(tree.xpath("//span[@itemprop='streetAddress']/text()")).strip()
    if "TX" in adr1:
        adr1 = adr1.split(",")[0]
    adr2 = "".join(tree.xpath("//span[@class='suite']/text()")).strip()
    street_address = f"{adr1} {adr2}".strip()
    city = "".join(tree.xpath("//span[@itemprop='addressLocality']/text()")).strip()
    state = "".join(tree.xpath("//span[@itemprop='addressRegion']/text()")).strip()
    postal = "".join(tree.xpath("//span[@itemprop='postalCode']/text()")).strip()
    country_code = "US"
    phone = "".join(tree.xpath("//span[@itemprop='telephone']/text()")).strip()
    latitude, longitude = geo.get(store_number)

    _tmp = []
    days = tree.xpath("//div[@class='days-of-week']/text()")
    times = tree.xpath("//div[@class='hours']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp)

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
    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in _ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://paciugo.com/"
    page_url = "https://paciugo.com/store-locator/"
    api = "https://paciugo.com/wp-admin/admin-ajax.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://paciugo.com",
        "Connection": "keep-alive",
        "Referer": "https://paciugo.com/store-locator/",
        "TE": "Trailers",
    }
    with SgRequests() as session:
        geo, _ids = get_param()
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
            fetch_data(writer)

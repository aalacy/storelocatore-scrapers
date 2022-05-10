from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_coords():
    out = dict()
    r = session.post(
        "https://www.famila.it/action/getStoresMapData", json=json_data, headers=headers
    )
    js = r.json()["features"]

    for j in js:
        p = j.get("properties") or {}
        _id = p.get("storeCode")
        _type = p.get("storeType")

        try:
            lng, lat = j["geometry"]["coordinates"]
        except:
            lat, lng = SgRecord.MISSING, SgRecord.MISSING

        out[_id] = {"lat": lat, "lng": lng, "type": _type}

    return out


def get_params():
    params = []
    r = session.post(
        "https://www.famila.it/action/getStoresList", headers=headers, json=json_data
    )
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-store-code]")
    for d in divs:
        _id = "".join(d.xpath("./@data-store-code"))
        slug = "".join(d.xpath("./@data-preferredstore-navigate"))
        url = f"https://www.famila.it{slug}"
        params.append((_id, url))

    return params


def get_data(param, sgw: SgWriter):
    store_number, page_url = param
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//span[@class='h5 primary']/text()")).strip()
    raw_address = " ".join(
        " ".join(tree.xpath("//h5[@class='title']/following-sibling::p/text()")).split()
    )
    line = tree.xpath("//h5[@class='title']/following-sibling::p/text()")
    line = list(filter(None, [li.strip() for li in line]))
    street_address = line.pop(0)
    cs = line.pop()
    if "(" in cs:
        city = cs.split("(")[0].strip()
        state = cs.split("(")[-1].replace(")", "").strip()
    else:
        city = cs
        state = SgRecord.MISSING

    if "-" in city:
        city = city.split("-")[0].strip()

    country_code = "IT"
    phone = "".join(
        tree.xpath("//ul[@class='show-for-large store-detail-contact']/li[1]//a/text()")
    ).strip()
    if "fax" in phone:
        phone = phone.split("fax")[0].strip()
    if " - " in phone and phone.count("/") >= 2:
        phone = phone.split(" - ")[0].strip()
    phone = phone.replace("tel", "").replace(".", "").strip()

    j = coords.get(store_number) or {}
    location_type = j.get("type")
    latitude = j.get("lat")
    longitude = j.get("lng")

    _tmp = []
    hours = tree.xpath("//li[contains(@class, 'cell store-opening-item')]")
    for h in hours:
        day = "".join(h.xpath("./div[1]//text()")).strip()
        inter = "|".join(h.xpath("./div[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        location_type=location_type,
        raw_address=raw_address,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    json_data = {
        "bounds": {
            "south": 26.481238561109123,
            "west": -44.153074375,
            "north": 53.781729674932336,
            "east": 69.577394375,
        },
        "openToday": False,
        "servicesFilter": [],
        "brandsFilter": [
            "FAMILA",
            "FAMILASUPERSTORE",
            "IPERFAMILA",
            "FAMILAMARKET",
        ],
        "typesFilter": [],
        "partnersFilter": [],
        "uuid": "2b79133b-8182-48c2-b75b-41c1f25d6a25",
        "registration": False,
    }

    coords = get_coords()
    locator_domain = "https://www.famila.it/"

    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

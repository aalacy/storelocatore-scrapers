import json5
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_params():
    params = []
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    script = "".join(
        tree.xpath("//script[contains(text(), 'markersCoords.push(')]/text()")
    )
    lines = script.split("markersCoords.push(")[1:-2]

    for line in lines:
        text = line.split(");")[0]
        j = json5.loads(text)
        lat = j.get("lat")
        lng = j.get("lng")
        _id = j.get("id")
        params.append({"id": _id, "lat": lat, "lng": lng})

    return params


def get_data(p, sgw: SgWriter):
    store_number = p.get("id")
    api = f"https://stores.boldapps.net/front-end/get_store_info.php?shop=tj-hughes-store.myshopify.com&data=detailed&store_id={store_number}"
    r = session.get(api)
    source = r.json()["data"]
    tree = html.fromstring(source)

    location_name = "".join(tree.xpath("//span[@class='name']/text()")).strip()
    street_address = ", ".join(
        tree.xpath("//span[contains(@class, 'address')]/text()")
    ).strip()
    city = "".join(tree.xpath("//span[@class='city']/text()")).strip()
    postal = "".join(tree.xpath("//span[@class='postal_zip']/text()")).strip()
    country_code = "GB"
    phone = "".join(tree.xpath("//span[@class='phone']/text()")).strip()

    latitude = p.get("lat")
    longitude = p.get("lng")

    _tmp = []
    hours = tree.xpath("//span[@class='hours']/text()")
    for h in hours:
        if not h.strip():
            continue
        _tmp.append(h.strip())
        if "Sun" in h:
            break

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
        locator_domain=locator_domain,
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
    locator_domain = "https://www.tjhughes.co.uk/"
    page_url = "https://www.tjhughes.co.uk/apps/store-locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

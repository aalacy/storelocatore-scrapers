import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hoo(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    _tmp = []
    hours = tree.xpath(
        "//div[@class='group-openinghours']/div[contains(@class, 'jour')]"
    )
    for h in hours:
        day = "".join(h.xpath(".//text()")).strip()
        inter = "".join(h.xpath("./following-sibling::div[1]//text()")).strip()
        if inter == "-":
            continue
        _tmp.append(f"{day} {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.intermarche.be/fr/store/shoplocator/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'Drupal.settings')]/text()"))
    text = text.split('"stores":')[1].split('"square":')[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        location_name = j.get("store")
        a = j.get("address") or {}
        street_address = a.get("street")
        city = a.get("locality")
        postal = a.get("postal_code")
        country_code = "BE"
        store_number = j.get("nid")
        page_url = j.get("alias")
        phone = j.get("phone") or ""
        if "-" in phone:
            phone = phone.split("-")[0].strip()
        latitude = j.get("lat")
        longitude = j.get("lon")
        hours_of_operation = get_hoo(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.intermarche.be/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

import json
from html import unescape
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
    hours = tree.xpath("//ul[@itemprop='openingHours']/li")
    for h in hours:
        day = "".join(h.xpath("./div[1]//text()")).strip()
        inter = "".join(h.xpath("./div[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.leaderprice-martinique.com/nos-magasins"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div/@data-locations"))
    js = json.loads(unescape(text))

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        postal = j.get("cp")
        country_code = "MQ"
        store_number = j.get("Id")
        location_name = j.get("name")
        slug = j.get("url")
        page_url = f"https://www.leaderprice-martinique.com{slug}"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
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
    locator_domain = "https://www.leaderprice-martinique.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

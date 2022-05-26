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
    hours = tree.xpath("//h3[contains(text(), 'Horaires')]/following-sibling::ul/li")
    for h in hours:
        _tmp.append(" ".join("".join(h.xpath(".//text()")).split()))

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://location.intermarche.com/nos-agences/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations =')]/text()"))
    text = text.split("var locations =")[1].strip()[:-1]
    js = json.loads(text).values()

    for j in js:
        adr1 = j.get("lp_address") or ""
        adr2 = j.get("lp_address2") or ""
        street_address = f"{adr1} {adr2}".replace('"', "").strip()
        city = j.get("lp_city")
        postal = j.get("lp_zipcode")
        country_code = "FR"
        store_number = j.get("id")
        name = j.get("wp_owner_label") or ""
        location_name = f"{name} {city}"
        slug = j.get("wplien")
        page_url = f"https://location.intermarche.com{slug}"
        phone = j.get("lp_tel") or ""
        latitude = j.get("lp_latitude")
        longitude = j.get("lp_longitude")
        try:
            hours_of_operation = get_hoo(page_url)
        except:
            hours_of_operation = SgRecord.MISSING

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://intermarche.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

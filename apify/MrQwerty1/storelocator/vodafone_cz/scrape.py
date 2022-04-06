import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.vodafone.cz/prodejny/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), ' var stores =')]/text()"))
    text = text.split("var stores =")[1].split("allCities")[0].strip()[:-1]
    js = json.loads(text)

    for j in js:
        location_name = j.get("name")
        slug = j.get("identifier") or ""
        page_url = f"https://www.vodafone.cz/prodejny/detail-prodejny/{slug}/"
        location_type = j.get("store_type")
        store_number = j.get("gx_code")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = j.get("phone")
        street_address = j.get("address_street") or ""
        street_address = street_address.replace("<br />", " ")
        city = j.get("address_city")
        postal = j.get("address_zip")
        hours = j.get("opening_hours") or {}

        _tmp = []
        for k, v in hours.items():
            try:
                inter = v[0].get("range")
                _tmp.append(f"{k}: {inter}")
            except:
                pass

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="CZ",
            phone=phone,
            store_number=store_number,
            latitude=latitude,
            longitude=longitude,
            location_type=location_type,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.vodafone.cz/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

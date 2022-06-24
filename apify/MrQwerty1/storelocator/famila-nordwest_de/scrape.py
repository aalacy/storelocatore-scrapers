import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.famila-nordwest.de/unsere-maerkte/marktsuche"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var marketsData =')]/text()"))
    text = text.split("var marketsData =")[1].split("}];")[0] + "}]"
    js = json.loads(text)

    for j in js:
        street_address = j.get("street")
        city = j.get("city") or ""
        postal = j.get("zip")
        country_code = "DE"
        store_number = j.get("bonialStoreId")
        location_name = j.get("name")
        slug = j.get("url")
        page_url = f"https://www.famila-nordwest.de{slug}"
        phone = j.get("phone")

        g = j.get("geo") or {}
        latitude = g.get("lat")
        longitude = g.get("lng")

        _tmp = []
        hours = j.get("openingHours") or {}
        for k, v in hours.items():
            _tmp.append(f'{k}: {"|".join(v)}')

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city.strip(),
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
    locator_domain = "https://www.famila-nordwest.de/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_cats():
    cats = dict()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'var asl_categories =')]/text()")
    )
    text = text.split("var asl_categories =")[1].split("}};")[0] + "}}"
    js = json.loads(text).values()
    for j in js:
        _id = j.get("id")
        name = j.get("name")
        cats[_id] = name

    return cats


def fetch_data(sgw: SgWriter):
    cats = get_cats()
    api = "https://www.alcivia.com/wp-content/uploads/agile-store-locator/locator-data.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("title")
        street_address = j.get("street")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "US"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        store_number = j.get("id")

        if "Grain:" in phone:
            phone = phone.split("Grain:")[-1].strip()

        _tmp = []
        types = j.get("categories") or ""
        for t in types.split(","):
            t = t.strip()
            cat = cats.get(t)
            if cat:
                _tmp.append(cat)
        location_type = ", ".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.alcivia.com/"
    page_url = "https://www.alcivia.com/connect/locations/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

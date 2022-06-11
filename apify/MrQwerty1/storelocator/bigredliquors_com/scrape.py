import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'cityHiveWidgetAPIResourceStorage')]/text()"
        )
    )
    text = text.replace("\\", "").split('"merchant_configs":')[1].split("}],")[0] + "}]"
    js = json.loads(text)

    for j in js:
        j = j.get("merchant")
        location_name = j.get("name") or ""
        status = j.get("onboarding_state")
        if status != "active":
            continue
        if location_name.lower().find("big red #") == -1:
            continue
        a = j.get("address")
        street_address = a.get("street_address")
        city = a.get("city")
        state = a.get("state")
        postal = a.get("zipcode")
        country_code = a.get("country_code")
        store_number = location_name.split("#")[1].split()[0]
        phone = j.get("phone_number")
        loc = a.get("address_properties") or {}
        latitude = loc.get("lat")
        longitude = loc.get("lng")
        location_type = j.get("type")

        _tmp = []
        hours = j.get("business_hours")
        for k, v in hours.items():
            if v.get("opening"):
                _tmp.append(f'{k}: {v.get("opening")} - {v.get("closing")}')
            else:
                _tmp.append(f"{k}: Closed")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            location_type=location_type,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://bigredliquors.com/"
    page_url = "https://bigredliquors.com/store-locator/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

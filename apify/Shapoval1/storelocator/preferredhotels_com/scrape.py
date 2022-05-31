import json
from sgscrape.sgrecord import SgRecord
from lxml import html
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://preferredhotels.com/"
    api_url = "https://headless.preferredhotels.com/api/v1/PropertySearch?site=PreferredHotels"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["properties"]

    for j in js.values():
        a = j.get("field_address")
        slug = j.get("entity_url")
        page_url = f"https://preferredhotels.com{slug}"
        location_name = j.get("title") or "<MISSING>"
        street_address = a.get("address_line1") or "<MISSING>"
        state = j.get("field_state_name") or "<MISSING>"
        country_code = a.get("country_code") or "<MISSING>"
        city = a.get("locality") or "<MISSING>"
        store_number = j.get("nid") or "<MISSING>"
        ll = j.get("field_geolocation")
        latitude = ll.get("lat") or "<MISSING>"
        longitude = ll.get("lng") or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        js_block = "".join(tree.xpath('//script[@type="application/json"]/text()'))
        js = json.loads(js_block)
        try:
            postal = (
                js.get("props")
                .get("pageProps")
                .get("nodeContent")
                .get("fieldAddress")
                .get("postalCode")
            )
        except AttributeError:
            postal = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)

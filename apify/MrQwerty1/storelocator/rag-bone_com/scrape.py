import json

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://www.rag-bone.com/stores"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//main/@data-stores-model"))
    js = json.loads(text)["stores"]

    for j in js:
        adr1 = j.get("address1") or ""
        adr2 = j.get("address2") or ""
        adr3 = j.get("address3") or ""

        raw_address = " ".join(f"{adr1} {adr2} {adr3}".split())
        street_address = f"{adr1} {adr2}".strip()
        city = j.get("city")

        state = SgRecord.MISSING
        if "," in adr3 and "/" in adr3:
            state = adr3.split(",")[-1].split("/")[0].strip()
        postal = j.get("postalCode") or SgRecord.MISSING
        country_code = j.get("countryCode") or ""

        if country_code == "AU" and postal == SgRecord.MISSING:
            street_address, postal = street_address.split(city)

        if country_code == "AU" and (not state.isupper() or state == SgRecord.MISSING):
            postal = postal.strip()
            state, postal = postal.split()

        store_number = j.get("ID")
        location_name = j.get("name")
        page_url = f"https://www.rag-bone.com/store-details?storeID={store_number}"
        phone = j.get("phone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        _tmp = []
        source = j.get("storeHours") or "<html>"
        root = html.fromstring(source)
        hours = root.xpath("//text()")
        for h in hours:
            if not h.strip() or "Regular" in h:
                continue
            _tmp.append(h.strip())

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
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rag-bone.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    with SgRequests() as session:
        with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
            fetch_data(writer)

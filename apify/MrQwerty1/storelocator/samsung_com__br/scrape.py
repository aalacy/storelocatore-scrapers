import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.samsung.com/br/campaign/storecontacts/"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var store =')]/text()"))
    text = text.split("var store =")[1].split("];")[0] + "]"
    js = json.loads(text)

    for j in js:
        street_address = j.get("endereco") or ""
        street_address = " ".join(street_address.split())
        city = j.get("cidade")
        state = j.get("estado")
        country_code = "BR"
        location_name = j.get("nome")
        p = j.get("contato") or ""
        try:
            phone = p.split("phone=")[-1].split("&")[0]
        except IndexError:
            phone = SgRecord.MISSING

        _types = []
        if j.get("drive") == "sim":
            _types.append("drive")
        if j.get("rappi") == "sim":
            _types.append("rappi")
        location_type = ",".join(_types)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            country_code=country_code,
            location_type=location_type,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.samsung.com/br"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)

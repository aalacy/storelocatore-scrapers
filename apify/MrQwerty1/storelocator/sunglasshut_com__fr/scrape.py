import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.sunglasshut.com/fr/trends/magasins"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var actual_JSON =')]/text()"))
    text = text.split("var actual_JSON =")[1].split("// init()")[0]
    js = json.loads(text)

    for j in js:
        location_name = j.get("MALL")
        store_number = j.get("SAP")
        location_type = j.get("Store Type")
        city = j.get("CITY")
        state = j.get("STATE")
        line = j.get("ADDRESS") or ""
        postal = line.split()[0]
        street_address = line.replace(postal, "").strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            store_number=store_number,
            location_type=location_type,
            country_code="FR",
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.sunglasshut.com/fr"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)

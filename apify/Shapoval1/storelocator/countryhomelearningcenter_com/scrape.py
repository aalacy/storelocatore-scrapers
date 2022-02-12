import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://countryhomelearningcenter.com"
    page_url = "https://countryhomelearningcenter.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    block1 = (
        "".join(tree.xpath('//script[contains(text(), "7611 W Loop")]/text()'))
        .split("addresses: ")[1]
        .split("],")[0]
        + ","
    )
    block2 = (
        "".join(tree.xpath('//script[contains(text(), "13120 US-183")]/text()'))
        .split("addresses: [")[1]
        .split("],")[0]
        + "]"
    )
    block = block1 + block2
    js = json.loads(block)
    for j in js:

        ad = "".join(j.get("address"))
        a = html.fromstring(ad)

        adr = a.xpath("//*/text()")
        if len(adr) == 5:
            del adr[0]

        street_address = "".join(adr[1]).replace("\n", "").replace(",", "").strip()
        phone = "".join(adr[3]).replace("\n", "").strip()
        adrr = "".join(adr[2]).replace("\n", "").strip()

        city = adrr.split(",")[0].strip()
        state = adrr.split(",")[1].split()[0].strip()
        postal = adrr.split(",")[1].split()[-1].strip()

        country_code = "US"
        location_name = "".join(adr[0]).replace("\n", "").replace(",", "").strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = (
            " ".join(tree.xpath('//p[contains(text(), "open from ")]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(hours_of_operation.split())
            .split("open from")[1]
            .split(",")[0]
            .replace(" until ", " - ")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

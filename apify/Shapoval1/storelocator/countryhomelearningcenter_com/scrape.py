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
        ad = html.fromstring(ad)
        ad = ad.xpath("//*/text()")
        if len(ad) == 5:
            ad = list(ad)
            del ad[0]

        street_address = "".join(ad[1]).replace("\n", "").replace(",", "").strip()
        phone = "".join(ad[3]).replace("\n", "").strip()
        adr = "".join(ad[2]).replace("\n", "").strip()

        city = adr.split(",")[0].strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[-1].strip()

        country_code = "US"
        location_name = "".join(ad[0]).replace("\n", "").replace(",", "").strip()
        latitude = j.get("latitude")
        longitude = j.get("longitude")

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
            hours_of_operation=SgRecord.MISSING,
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

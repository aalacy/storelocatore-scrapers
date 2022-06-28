from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.daisosingapore.com.sg/store"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//li[contains(@class, 'store_list__item') and ./h3]")
    for d in divs:
        location_name = "".join(d.xpath("./h3/text()")).strip()
        line = d.xpath(".//dd//text()")
        line = list(filter(None, [l.strip() for l in line]))
        raw_address = line.pop(0)
        hours = line.pop(0)
        if line:
            phone = line.pop(0)
        else:
            phone = SgRecord.MISSING

        zc = raw_address.split(", ")[-1]
        street_address = ", ".join(raw_address.split(", ")[:-1])
        postal = zc.split()[-1]
        city = zc.replace(postal, "").strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="SG",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.daisosingapore.com.sg/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='find-shop-item']")

    for d in divs:
        location_name = d.xpath(".//div[@class='address-blog']/h4/text()")[0].strip()
        line = d.xpath(".//div[@class='address-blog'][1]/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = line.pop()
        csz = line.pop().replace(" CA ", ", CA ").split(", ")
        postal = csz[1].split()[-1]
        state = csz[1].replace(postal, "").strip()
        city = csz.pop(0)
        street_address = ", ".join(line)
        hours_of_operation = ";".join(
            d.xpath(".//h4[text()='HOURS']/following-sibling::p/text()")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.goorin.com/"
    page_url = "https://www.goorin.com/pages/goorin-retail-locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)

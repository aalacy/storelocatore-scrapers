from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dennysmexico.com/"
    api_url = "https://dennysmexico.com/sucursales/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[@itemprop="headline"]')
    for d in div:

        page_url = "https://dennysmexico.com/sucursales/"
        location_name = "".join(d.xpath(".//text()"))
        ad = "".join(d.xpath('.//preceding::h3[@itemprop="headline"][1]/text()'))
        adr = d.xpath('.//following::div[@itemprop="text"][1]/p/text()')
        street_address = "".join(adr[0]).strip()
        if len(adr) > 2:
            street_address = "".join(adr[1]).replace("\n", "").strip()
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "Mexico"
        city = ad
        if ad.find(",") != -1:
            city = ad.split(",")[0].strip()
            state = ad.split(",")[1].strip()
        phone = "".join(adr[-1]).replace("\n", "").strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

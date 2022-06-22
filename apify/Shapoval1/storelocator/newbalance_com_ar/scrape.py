from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.newbalance.com.ar/"
    page_url = "https://www.newbalance.com.ar/locales/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="card_location"]')
    for d in div:
        slug = "".join(d.xpath(".//p[@data-lat]/text()"))
        location_name = "New Balance Store"
        if slug.find("Outlet") != -1:
            location_name = "New Balance Outlet"
        ad = (
            "".join(d.xpath(".//ul/li[1]/text()"))
            .replace("\n", "")
            .replace("\r", " ")
            .strip()
        )
        street_address = ad.split(",")[0].strip()
        state = ad.split(",")[2].strip()
        country_code = "AR"
        city = ad.split(",")[1].strip()
        latitude = "".join(d.xpath(".//p/@data-lat"))
        longitude = "".join(d.xpath(".//p/@data-lng"))
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        if phone.find("interno") != -1:
            phone = phone.split("interno")[0].strip()
        hours_of_operation = (
            "".join(d.xpath(".//ul/li[2]/text()"))
            .replace("\n", "")
            .replace("\r", " ")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

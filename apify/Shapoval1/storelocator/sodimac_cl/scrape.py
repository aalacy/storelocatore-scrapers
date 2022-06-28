from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://sodimac.cl/"
    page_url = (
        "https://sodimac.falabella.com/sodimac-cl/page/tiendas-y-horarios-sodimac"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[contains(@class, "AccordeonItems-module_card-item")]')
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()")).replace("\n", "").strip()
        ad = (
            "".join(
                d.xpath(
                    './/div[contains(@class, "Accordion-module_content-text")]/span[1]/p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        street_address = " ".join(ad.split(",")[:-1]).strip()
        state = "".join(
            d.xpath(
                './/preceding::span[contains(@class, "AccordeonItems-module_title-accordion")][1]//text()'
            )
        )
        postal = "<MISSING>"
        country_code = "CL"
        city = ad.split(",")[-1].replace(".", "").strip()
        if city.find("Errázuriz Nº 700 Cauquenes") != -1:
            street_address = street_address + " Errázuriz Nº 700"
            city = "Cauquenes"
        info = d.xpath(".//text()")
        info = list(filter(None, [a.strip() for a in info]))
        tmp = []
        for i in info:
            if "hrs." in i or "cerrado" in i or "Cerrado" in i:
                tmp.append(i)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)

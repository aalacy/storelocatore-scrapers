from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://honda.bg/"
    api_url = "https://cars.honda.bg/dealers/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="vc_tta-tabs-list"]/li/a')
    for d in div:
        id_s = "".join(d.xpath(".//@href")).replace("#", "").strip()
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://cars.honda.bg/dealers/{slug}"
        location_name = "".join(d.xpath(f'.//following::div[@id="{id_s}"]//h3//text()'))
        ad = "".join(
            d.xpath(
                f'.//following::div[@id="{id_s}"]//h3/following-sibling::p[1]/text()'
            )
        )
        street_address = "".join(
            d.xpath(
                f'.//following::div[@id="{id_s}"]//h3/following-sibling::p[2]/text()'
            )
        )
        postal = ad.split()[0].strip()
        country_code = "BG"
        city = ad.split()[1].strip()
        phone_list = d.xpath(
            f'.//following::div[@id="{id_s}"]//p[contains(text(), "тел")]//text()'
        )
        phone_list = list(filter(None, [a.strip() for a in phone_list]))
        phone = " ".join(phone_list).replace("централа", "").strip()
        if phone.count("тел.:") > 1:
            phone = phone.split("тел.:")[1].strip()
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    f'.//following::div[@id="{id_s}"]//p[./span/strong[text()="Работно време"]]/following-sibling::p[position() < last()]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

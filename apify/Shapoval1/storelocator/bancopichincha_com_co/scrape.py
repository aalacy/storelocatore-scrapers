from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bancopichincha.com.co/"
    api_url = "https://www.bancopichincha.com.co/web/corporativo/red-de-oficinas"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="offices"]//div[@class="media-body"]/div')
    for d in div:
        block = d.xpath('./div[@class="oficina"]')
        city = "".join(d.xpath("./@id"))
        if city.find("-") != -1:
            city = city.split("-")[1].capitalize().strip()
        for b in block:
            page_url = (
                "https://www.bancopichincha.com.co/web/corporativo/red-de-oficinas"
            )
            location_name = "".join(b.xpath(".//h4//text()"))
            street_address = (
                "".join(b.xpath(".//ul/li[1]/text()")).replace("\n", "").strip()
            )
            country_code = "CO"
            text = "".join(b.xpath('.//div[@class="llegar-m"]/a/@href'))
            try:
                latitude = text.split("ll=")[1].split("%2C")[0].strip()
                longitude = text.split("ll=")[1].split("%2C")[1].split("&")[0].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            phone = (
                "".join(b.xpath('.//ul/li[contains(text(), "Teléfono")]/text()'))
                .replace("Teléfono:", "")
                .strip()
            )
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            hours_of_operation = (
                "".join(b.xpath(".//ul/li[2]/text()"))
                .replace("Horario:", "")
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
                zip_postal=SgRecord.MISSING,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)

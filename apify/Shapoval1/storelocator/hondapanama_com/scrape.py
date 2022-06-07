from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hondapanama.com"
    api_url = "https://www.hondapanama.com/localiza-tu-sucursal"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="locations"]/div')
    for d in div:

        page_url = "https://www.hondapanama.com/localiza-tu-sucursal"
        location_name = (
            "".join(d.xpath('.//span[@class="Service-locator_name"]/text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            " ".join(
                d.xpath('.//p[contains(text(), "Tel")]/preceding-sibling::p/text()')
            )
            .replace("\n", "")
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "PA"
        city = a.city or "<MISSING>"
        latitude = "".join(d.xpath(".//@data-lat"))
        longitude = "".join(d.xpath(".//@data-lng"))
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Tel")]/text()'))
            .replace("Tel:", "")
            .strip()
        )
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[./b[text()="VENTAS DE AUTOS"]]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .replace("\r", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

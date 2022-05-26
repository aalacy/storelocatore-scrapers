from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sodimac.cl/"
    page_url = "https://www.sodimac.cl/sodimac-cl/content/a60055/tiendas-sodimac/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//table[@class="table"]//tr[./td[contains(@class, "text-center")]]'
    )
    for d in div:

        location_name = "".join(d.xpath(".//h3//text()"))
        ad = (
            "".join(d.xpath(".//span/following-sibling::text()"))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "CL"
        city = a.city or "<MISSING>"
        hours_of_operation = (
            "Lunes a Viernes "
            + "".join(d.xpath(".//td[2]//text()"))
            + " - "
            + "".join(d.xpath(".//td[3]//text()"))
            + " Sábado "
            + "".join(d.xpath(".//td[4]//text()"))
            + " - "
            + "".join(d.xpath(".//td[5]//text()"))
            + " Domingo "
            + "".join(d.xpath(".//td[6]//text()"))
            + " - "
            + "".join(d.xpath(".//td[7]//text()"))
        )
        hours_of_operation = hours_of_operation.replace(
            "CERRADO -  CERRADO", "CERRADO"
        ).strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

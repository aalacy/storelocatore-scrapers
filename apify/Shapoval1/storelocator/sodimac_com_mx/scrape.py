from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sodimac.com.mx/"
    api_url = "https://www.sodimac.com.mx/sodimac-mx/content/a1430001/Tiendas/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[contains(@id, 'map')]")
    for d in div:

        page_url = "".join(d.xpath('.//a[.//p[contains(text(), "más info")]]/@href'))
        location_name = (
            "".join(d.xpath('./p[@class="homeCenterTitle"][1]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = (
            " ".join(d.xpath('./p[@class="homeCenter"][1]//text()'))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        street_address = str(street_address).replace("Estado De México.", "").strip()
        state = a.state or "<MISSING>"
        state = str(state).replace(".", "").strip()
        postal = a.postcode or "<MISSING>"
        postal = str(postal).replace("CP.", "").strip()
        country_code = "MX"
        city = (
            "".join(d.xpath('.//preceding::p[@class="titulosTiendas"][1]//text()'))
            .replace("\n", "")
            .strip()
        )
        if city == "Puntos Pick Up":
            city = a.city or "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[contains(text(), "Horarios")]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://supertiendascanaveral.com.co/"
    api_url = "https://supertiendascanaveral.com.co/nuestras-sedes/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h2/following::a[contains(@href, "w7z")]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        city = (
            "".join(d.xpath(".//preceding::h2[1]//text()")).replace("SEDES", "").strip()
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            " ".join(tree.xpath("//h2//text()")).replace("\n", " ").strip()
            or "<MISSING>"
        )
        street_address = (
            "".join(
                tree.xpath(
                    '//div[./span/i[@class="fas fa-map-marker-alt"]]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .replace("Dirección:", "")
            .strip()
        )
        country_code = "CO"
        phone = (
            "".join(
                tree.xpath(
                    '//div[./span/i[@class="fas fa-phone-alt"]]/following-sibling::div[1]//text()'
                )
            )
            .replace("Teléfono Sede:", "")
            .replace(" Ext.", "")
            .replace("Ext", "")
            .replace("Ext:", "")
            .replace("y 610", "")
            .replace(" : ", "")
            .replace("-", "")
            .replace(" ", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//div[./span/i[@class="far fa-clock"]]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .replace("Horarios:", "")
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

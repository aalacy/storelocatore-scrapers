from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.ippudo.fr"
    api_url = "https://www.ippudo.fr/info/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "column store")]')
    for d in div:
        slug = "".join(d.xpath('.//a[./img[@alt="Click & Collect."]]/@href'))
        page_url = f"https://www.ippudo.fr{slug}"

        location_name = "".join(d.xpath('.//h5[@class="store__name"]/text()'))
        street_address = "".join(d.xpath(".//h5/following-sibling::p[1]/text()[1]"))
        ad = (
            "".join(d.xpath(".//h5/following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        postal = ad.split()[0].strip()
        country_code = "FR"
        city = ad.split()[1].strip()
        phone = (
            "".join(d.xpath(".//h5/following-sibling::p[1]/text()[3]"))
            .replace("\n", "")
            .replace("Tel:", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/li[./u[contains(text(), "Horaires d’ouverture")]]/following-sibling::li/text()'
                )
            )
            .replace("\n", "")
            .split("*")[0]
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

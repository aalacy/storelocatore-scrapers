from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.memoria.ca/"
    api_url = "https://www.memoria.ca/en/funeral-complexes-cemeteries.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//article[@class="wrapper-succursale"]')
    for d in div:
        slug = "".join(d.xpath(".//h3/a/@href"))
        page_url = f"https://www.memoria.ca/{slug}"
        location_name = "".join(d.xpath(".//h3/a/text()"))
        latitude = (
            "".join(d.xpath('.//a[@class="lien-pin no-print"]/@href'))
            .split("=")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(d.xpath('.//a[@class="lien-pin no-print"]/@href'))
            .split("=")[1]
            .split(",")[1]
            .strip()
        )
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        street_address = (
            "".join(
                tree.xpath(
                    '//h3[@class="titre1-succursale"]/following-sibling::p[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//h3[@class="titre1-succursale"]/following-sibling::p[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split("(")[1].split(")")[0].replace(",", "").strip()
        postal = ad.split(")")[1].strip()
        country_code = "CA"
        city = ad.split("(")[0].replace(",", "").strip()

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
            hours_of_operation=SgRecord.MISSING,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://cinnabon.cz"
    api_url = "https://cinnabon.cz/najdi-cinnabon/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p[contains(text(), "Tel")]]')
    for d in div:

        page_url = "https://cinnabon.cz/najdi-cinnabon/"
        location_name = "".join(d.xpath(".//strong/text()"))
        street_address = (
            "".join(d.xpath(".//strong/following-sibling::text()[1]"))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        postal = (
            "".join(d.xpath(".//strong/following-sibling::text()[2]"))
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )
        country_code = "CZ"
        city = (
            "".join(d.xpath(".//strong/following-sibling::text()[3]"))
            .replace("\n", "")
            .split()[0]
            .strip()
        )
        text = "".join(d.xpath('.//following::a[contains(@href, "maps")][1]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Tel.:")]/text()'))
            .replace("Tel.:", "")
            .strip()
        )
        hours_of_operation = (
            "".join(d.xpath(".//p[.//b]//text()")).replace("\n", "").strip()
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

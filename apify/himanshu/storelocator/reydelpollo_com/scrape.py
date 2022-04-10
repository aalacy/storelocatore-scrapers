from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    locator_domain = "reydelpollo.com"
    api_url = "https://reydelpollo.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./p/a[contains(@href, "tel")]]')
    for d in div:

        page_url = "https://reydelpollo.com/locations/"
        location_name = "".join(d.xpath(".//h4/text()[1]")) or "<MISSING>"
        address = (
            "".join(d.xpath(".//h4/text()[2]")).replace("\n", "").strip() or "<MISSING>"
        )
        street_address = address.split(",")[0].strip()
        state = address.split(",")[2].split()[0].strip()
        postal = address.split(",")[2].split()[1].strip()
        country_code = "US"
        city = address.split(",")[1].strip()
        map_link = "".join(d.xpath(".//following::iframe[1]/@data-src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//p[contains(text(), "Hours:")]/text()'))
            .replace("\n", "")
            .replace("Hours:", "")
            .strip()
            or "<MISSING>"
        )

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
            raw_address=address,
        )
        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

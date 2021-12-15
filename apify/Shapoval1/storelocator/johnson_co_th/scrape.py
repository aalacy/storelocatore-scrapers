from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnson.co.th"
    api_url = "https://johnson.co.th/all-stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h4]")
    for d in div:

        page_url = "https://johnson.co.th/all-stores/"
        location_name = "".join(d.xpath(".//h4/text()"))
        ad = (
            "".join(d.xpath('.//i[@class="icon-location"]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
        )
        if ad.find("Tel") != -1:
            ad = ad.split("Tel")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("ิ ", "")
            .replace("None", "")
            .strip()
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "TH"
        city = a.city or "<MISSING>"
        map_link = "".join(d.xpath(".//preceding::iframe[1]/@nitro-lazy-src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(d.xpath('.//i[@class="icon-call"]/following-sibling::text()'))
            .replace("\n", "")
            .replace("โทร.", "")
            .strip()
        )
        if phone.find(",") != -1:
            phone = phone.split(",")[0].strip()
        if phone.find("ต่อ") != -1:
            phone = phone.split("ต่อ")[0].strip()
        hours_of_operation = (
            "".join(d.xpath('.//i[@class="icon-clock"]/following-sibling::text()'))
            .replace("\n", "")
            .strip()
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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)

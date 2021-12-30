from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.grandandtoy.com"
    api_url = "https://www.grandandtoy.com/en/sites/core/branch-offices"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//main[@id="main-content"]//h4')
    for d in div:

        page_url = "https://www.grandandtoy.com/en/sites/core/branch-offices"
        location_name = "".join(d.xpath(".//text()"))
        ad = (
            " ".join(d.xpath(".//following-sibling::p[1]/text()"))
            .replace("\n", "")
            .split("Tel:")[0]
            .strip()
        )
        street_address = ad.split(",")[0].strip()
        state = "".join(d.xpath(".//preceding::h2[1]/text()"))
        postal = ad.split(",")[2].strip()
        country_code = "CA"
        city = ad.split(",")[1].strip()
        if city.find("Unit 101") != -1:
            street_address = street_address + " " + "Unit 101"
            city = city.replace("Unit 101", "").strip()
        if ad.count(",") == 3:
            street_address = " ".join(ad.split(",")[:2]).strip()
            city = ad.split(",")[2].strip()
            postal = ad.split(",")[3].strip()
        phone = (
            " ".join(d.xpath(".//following-sibling::p[1]/text()[last()]"))
            .replace("\n", "")
            .replace("Tel:", "")
            .strip()
        )
        if phone.find("|") != -1:
            phone = phone.split("|")[0].strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

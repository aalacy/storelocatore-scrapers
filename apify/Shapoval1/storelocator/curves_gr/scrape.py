from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curves.gr"
    api_url = "https://curves.gr/clubs/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h2/following::img[not(@class="hfe-retina-img elementor-animation-")]'
    )
    for d in div:

        page_url = "https://curves.gr/clubs/"
        location_name = "".join(d.xpath(".//following::h2[1]/text()"))
        str_adr = d.xpath(".//following::div[./p][1]/p//text()")
        str_adr = list(filter(None, [a.strip() for a in str_adr]))
        phone = str(str_adr[-1]).strip()
        if phone == "Νέα Ερυθαία 14 671":
            phone = "<MISSING>"
        if phone.find("&") != -1:
            phone = phone.split("&")[0].strip()

        street_address = "".join(d.xpath(".//following::p[1]/text()[1]"))
        ad = []
        for s in str_adr:
            if phone not in s:
                ad.append(s)
        adr = "".join(ad[-1]).strip()
        postal = adr.split()[-1].strip()
        if adr.count(" ") == 3 or adr.count(" ") == 2:
            postal = " ".join(adr.split()[-2:])
        country_code = "GR"
        city = adr.split()[0].strip()
        if adr.count(" ") == 3:
            city = " ".join(adr.split()[:2])
        hours_of_operation = "<MISSING>"
        if street_address.find("Σύντομα κοντά σας") != -1:
            hours_of_operation = "Coming Soon"
            street_address = "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)

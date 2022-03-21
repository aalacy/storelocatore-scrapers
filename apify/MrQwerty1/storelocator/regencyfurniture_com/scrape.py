from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.regencyfurniture.com/pages/store-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
    }

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='row']/div[@class='col-md-6']/p[./strong]")
    hours = tree.xpath("//hr/following-sibling::p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours = ";".join(hours) or SgRecord.MISSING

    for d in divs:
        hours_of_operation = hours
        location_name = "".join(d.xpath("./strong/text()")).strip()
        if "coming soon" in location_name.lower():
            hours_of_operation = "Coming Soon"
        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line.pop(0)
        if line[-1][0].isdigit():
            phone = line.pop()
        else:
            phone = SgRecord.MISSING

        line = line[0]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"

        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.regencyfurniture.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

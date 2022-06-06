from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    page_url = "https://www.boden.co.uk/en-gb/shopping-with-us/boden-shops"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//div[@class='richText-content' and ./h2 and ./p/a]")
    for d in divs:
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = line.pop(0)
        street_address = line.pop(0).replace(",", "")
        city = line.pop(0)
        if city == "London":
            state = "London"
        else:
            state = line.pop(0)
        postal = line.pop(0)
        text = "".join(d.xpath(".//a/@href"))
        try:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        line.pop()
        hours_of_operation = ";".join(line[line.index("OPENING HOURS") + 1 :])

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="GB",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.boden.co.uk/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)

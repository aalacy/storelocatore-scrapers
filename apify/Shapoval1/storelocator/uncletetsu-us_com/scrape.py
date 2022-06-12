from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.uncletetsu-us.com"
    page_url = "https://www.uncletetsu-us.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//table[@class="views-table views-view-table cols-0"]//tr')
    for d in div:

        location_name = "".join(d.xpath('.//div[@class="title"]/text()'))
        ad = d.xpath('.//div[@class="body"]//text()')
        ad = list(filter(None, [a.strip() for a in ad]))
        street_address = "<MISSING>"
        adr = "<MISSING>"
        if len(ad) < 5:
            street_address = "".join(ad[0])
            adr = "".join(ad[1])
        if len(ad) > 4:
            street_address = "".join(ad[1])
            adr = "".join(ad[2])

        phone = "<MISSING>"
        for i in ad:
            if "Phone" in i:
                phone = "".join(i).replace("Phone:", "").replace("\xa0", "").strip()
        state = adr.split(",")[1].split()[0].strip()
        postal = adr.split(",")[1].split()[1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = "<MISSING>"
        if location_name.find("CURRENTLY CLOSED") != -1:
            hours_of_operation = "CURRENTLY CLOSED"

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
            raw_address=f"{street_address} {adr}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.hawthorneonline.com/"
    api_url = "https://www.hawthorneonline.com/store-locator"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = "".join(tree.xpath("//input/@data-markersdata"))
    js = json.loads(div)
    for j in js:

        location_name = j.get("Name")
        store_number = j.get("Id")
        latitude = j.get("Latitude")
        longitude = j.get("Longitude")
        info = j.get("ShortDescription")
        a = html.fromstring(info)
        street_address = "".join(a.xpath("//p[1]/text()"))
        ad = "".join(a.xpath("//p[2]/text()"))
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = "".join(a.xpath("//p[3]/text()"))
        slug = "".join(
            tree.xpath(
                f'//li[@data-shopid="{store_number}"]//a[@class="shop-link"]/@href'
            )
        )
        page_url = f"https://www.hawthorneonline.com{slug}"
        hours = tree.xpath('//strong[contains(text(), "MONDAY")]/text()')
        hours_of_operation = "".join(hours[0]).strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
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

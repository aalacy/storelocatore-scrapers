from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitnessme.com"
    api_url = "https://johnsonfitnessme.com/contact/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    page_url = "https://johnsonfitnessme.com/contact/"
    ad = (
        " ".join(
            tree.xpath('//i[@class="las la-home fs__16"]/following-sibling::text()')
        )
        .replace("\n", "")
        .strip()
    )
    ad = " ".join(ad.split())
    street_address = " ".join(ad.split(",")[2].split()[:-1]).strip()
    country_code = "UAE"
    city = ad.split(",")[2].split()[-1]
    map_link = "".join(tree.xpath('//iframe[contains(@src, "maps")]/@src'))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    phone = (
        " ".join(
            tree.xpath('//i[@class="las la-phone fs__18"]/following-sibling::text()')
        )
        .replace("\n", "")
        .replace("JOHNSON ", "")
        .strip()
    )
    location_name = "".join(tree.xpath("//title/text()"))

    row = SgRecord(
        locator_domain=locator_domain,
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=SgRecord.MISSING,
        zip_postal=SgRecord.MISSING,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
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

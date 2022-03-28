from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://crowfootliquor.com"
    page_url = "https://crowfootliquor.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="entry"]/section[position()>1]')

    for d in div:

        location_name = "".join(d.xpath(".//h3/text()")).replace("hours", "").strip()
        if location_name.find("Aspen Wine & Spirits") != -1:
            continue
        location_type = "Crowfoot Wine & Spirits"
        street_address = " ".join(
            d.xpath('.//p[./a[contains(@href, "goo")]]/a/text()')
        ).strip()
        ad = (
            " ".join(d.xpath('.//p[./a[contains(@href, "goo")]]/text()'))
            .replace("\n", "")
            .strip()
        )
        if location_name.find("Altadore") != -1:
            ad = "Calgary, AB T2T 3W2"
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Phone")]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        country_code = "CA"
        city = ad.split(",")[0].strip()
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath('.//h3[text()="hours"]/following-sibling::p//text()'))
            .replace("\n", " ")
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
            location_type=location_type,
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

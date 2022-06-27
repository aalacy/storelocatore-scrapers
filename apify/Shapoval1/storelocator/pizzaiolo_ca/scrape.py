from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://pizzaiolo.ca"
    api_url = "https://pizzaiolo.ca/locations"
    session = SgRequests()

    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-card"]')

    for d in div:
        ad = d.xpath('.//div[@class="address"]/text()')
        street_address = "".join(ad[0])
        ad = "".join(ad[1]).strip()
        city = ad.split(",")[0].strip()
        postal = " ".join(ad.split(",")[1].split()[1:]).strip()
        state = ad.split(",")[1].split()[0].strip()
        country_code = "CA"
        slug = "".join(d.xpath('.//a[contains(text(), "More Info")]/@href'))
        page_url = f"{locator_domain}{slug}"
        phone = "".join(d.xpath('.//a[contains(@href, "tel")]/text()'))
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        location_name = "".join(
            tree.xpath('//h2[@class="heading-green inner-page-sub-title"]/text()')
        )
        text = "".join(tree.xpath('//a[contains(@href, "maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        if street_address.find("707") != -1 or street_address.find("104") != -1:
            latitude = (
                "".join(tree.xpath('//img[@class="img-polaroid"]/@src'))
                .split("center=")[1]
                .split(",")[0]
            )
            longitude = (
                "".join(tree.xpath('//img[@class="img-polaroid"]/@src'))
                .split("center=")[1]
                .split(",")[1]
                .split("&")[0]
            )
        hours_of_operation = (
            " ".join(tree.xpath('//table[@class="hours"]//tr/td/text()'))
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
            raw_address=f"{street_address} {ad}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

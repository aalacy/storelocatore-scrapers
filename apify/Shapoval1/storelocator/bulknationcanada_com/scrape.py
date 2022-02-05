from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bulknationcanada.com"
    api_url = "https://bulknationcanada.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Details & Directions"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        page_url = slug
        if page_url.find("http") == -1:
            page_url = f"{locator_domain}{slug}"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()"))
        street_address = (
            "".join(
                tree.xpath(
                    '//div[@class="heading heading-with-icon icon-left"]//h2[text()="Location"]/following::*[./text()][1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath(
                    '//div[@class="heading heading-with-icon icon-left"]//h2[text()="Location"]/following::*[./text()][1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        adr = (
            "".join(
                tree.xpath(
                    '//div[@class="heading heading-with-icon icon-left"]//h2[text()="Location"]/following::*[./text()][1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//div[@class="heading heading-with-icon icon-left"]//h2[text()="Contact Infomation"]/following::*[./text()][1]/a/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = (
            "".join(
                tree.xpath(
                    '//div[@class="heading heading-with-icon icon-left"]//h2[text()="Contact Infomation"]/following::*[./text()][1]/text()'
                )
            )
            .replace("\n", "")
            .replace("Phone:", "")
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
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

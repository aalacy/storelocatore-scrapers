from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://jensensfoods.com/"
    api_url = "https://palmdesert.jensensfoods.com/locations/palm-desert/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="section_col col7"]/div/p[1]/a')
    for d in div:

        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://palmdesert.jensensfoods.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//article/h1/text()")) or "<MISSING>"
        ad = "".join(tree.xpath("//article/h1/following-sibling::p[1]/text()"))
        street_address = ad.split("•")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split("•")[1].split(",")[0].strip()
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//article/h1/following-sibling::p[contains(text(), "Manager")]/preceding-sibling::p[1]/text()'
                )
            ).strip()
            or "<MISSING>"
        )
        if phone.find("•") != -1:
            phone = phone.split("•")[0].strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//article/h1/following-sibling::p[contains(text(), "PM")]/text()'
                )
            )
            .replace("\n", "")
            .replace("Temporary Hours:", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

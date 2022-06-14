from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.theainsworth.com"
    api_url = "https://www.theainsworth.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@data-current-styles]//following::div[@class="container header-menu-nav-item"]/a'
    )

    for d in div:
        slug = "".join(d.xpath(".//@href"))
        if slug.find("locations") != -1:
            continue

        page_url = f"{locator_domain}{slug}"

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/text()"))
        ad = tree.xpath("//h1/following-sibling::*//text()")
        adr = "".join(ad[0]).strip()
        if "".join(ad).find("NOW OPEN!") != -1:
            adr = "".join(ad[1]).strip()
        if "".join(ad).find("COMING SOON") != -1:
            adr = "<MISSING>"
        adr = adr.replace("Rockville Centre", ",Rockville Centre").strip()
        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "USA"
        city = "<MISSING>"

        if adr != "<MISSING>":
            street_address = adr.split(",")[0].strip()
            city = adr.split(",")[1].strip()
            state = adr.split(",")[2].split()[0].strip()
            postal = adr.split(",")[2].split()[1].strip()

        phone = (
            "".join(tree.xpath("//h1/following-sibling::p[./a]/a/text()"))
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath("//h1/following-sibling::p/text()")) or "<MISSING>"
            )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="image-subtitle-wrapper"]//p/text() | //h3[./strong[text()="Hours of Operation "]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if "".join(ad).find("TEMPORARILY CLOSED") != -1:
            hours_of_operation = "Temporarily Closed"
        if "".join(ad).find("COMING SOON") != -1:
            hours_of_operation = "Coming Soon"
        if hours_of_operation.find("Rooftop") != -1:
            hours_of_operation = hours_of_operation.split("Rooftop")[0].strip()
        if hours_of_operation.find("Entertainment") != -1:
            hours_of_operation = hours_of_operation.split("Entertainment")[0].strip()

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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

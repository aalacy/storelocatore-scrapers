from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://littlebigburger.com"

    api_url = "https://littlebigburger.com/locations-menus/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//a[contains(@href, "locations/")]')
    for b in block:

        slug = "".join(b.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h4//text()")).strip()
        street_address = "".join(tree.xpath("//h3/span[1]/text()"))
        if page_url.find("university-of-oregon") != -1:
            street_address = "".join(tree.xpath("//h3[1]/span[2]/text()[1]"))
        ll = "".join(
            tree.xpath(
                '//div[@class="et_pb_module et_pb_code et_pb_code_0"]//*[contains(@data-center, "-")]/@data-center'
            )
        )
        try:
            latitude = ll.split(",")[1]
            longitude = ll.split(",")[0]
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        country_code = "US"
        state = "".join(tree.xpath("//h3/span[3]/text()"))
        if page_url.find("/capitolhill/") != -1:
            state = "".join(tree.xpath("//h3/span[2]/span/text()"))
        state = state.replace("regon", "Oregon").replace(",", "").strip()
        if state == "orth Carolina":
            state = state.replace("orth Carolina", "North Carolina")
        postal = "".join(tree.xpath("//h3/span[4]/text()"))
        city = "".join(tree.xpath("//h3/span[2]/text()")).replace(",", "")
        if page_url.find("university-of-oregon") != -1:
            city = (
                "".join(tree.xpath("//h3[1]/span[2]/text()[2]"))
                .replace("\n", "")
                .split()[0]
                .strip()
            )
            state = (
                "".join(tree.xpath("//h3[1]/span[2]/text()[2]"))
                .replace("\n", "")
                .split()[1]
                .strip()
            )
            postal = (
                "".join(tree.xpath("//h3[1]/span[2]/text()[2]"))
                .replace("\n", "")
                .split()[2]
                .strip()
            )
        hours_of_operation = (
            "".join(tree.xpath('//h3[contains(text(), "Mon")]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                "".join(tree.xpath('//strong[contains(text(), "Mon")]/text()'))
                or "<MISSING>"
            )
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lolascupcakes.co.uk/"
    api_url = "https://www.lolascupcakes.co.uk/cupcakes/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store"]')
    for d in div:

        slug = "".join(d.xpath('.//a[text()="More info"]/@href'))
        page_url = f"https://www.lolascupcakes.co.uk{slug}"
        location_name = (
            "".join(d.xpath(".//h5//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        store_number = page_url.split("=")[-1].strip()
        latitude = "".join(d.xpath(".//*/@data-latitude"))
        longitude = "".join(d.xpath(".//*/@data-longitude"))
        phone = (
            "".join(d.xpath('.//p[@class="contact"]/text()'))
            .replace("Phone:", "")
            .replace("N/A", "")
            .strip()
            or "<MISSING>"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = (
            " ".join(tree.xpath('//div[@class="address"]/p//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        info_add = tree.xpath('//div[@class="address"]/p//text()')
        info_add = list(filter(None, [b.strip() for b in info_add]))
        postal = "".join(info_add[-1]).strip()
        country_code = "UK"
        city = "".join(info_add[-2]).replace(",", "").strip()
        street_address = " ".join(info_add[1:-2]).replace(",", "").strip()
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="openingtimes-items"]//text()'))
            .replace("&nbsp", " ")
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
        if hours_of_operation.find("Bank") != -1:
            hours_of_operation = hours_of_operation.split("Bank")[0].strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
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

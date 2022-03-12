from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.schweigerderm.com/"
    api_url = "https://www.schweigerderm.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//li[@class="col-6 col-xl-3 col-lg-4 col-md-6"]')
    for d in div:

        page_url = "".join(d.xpath("./a/@href"))
        location_name = "".join(d.xpath(".//h3//text()")).replace("\n", "").strip()
        ad = d.xpath(".//h3/following-sibling::p//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        adr = "".join(ad[-1]).replace("\n", "").replace("\r", "").strip()
        adr = " ".join(adr.split())
        street_address = " ".join(ad[:-1]).replace("\n", "").replace("\r", "").strip()
        state = " ".join(adr.split(",")[1].split()[:-1])
        postal = adr.split()[-1].strip()
        country_code = "US"
        city = adr.split(",")[0].strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//h1/following-sibling::p[1]//a[contains(@href, "tel")]//text()'
                )
            )
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@id="location-center"]/div[1]//text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("temporarily closed") != -1:
            hours_of_operation = "temporarily closed"

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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

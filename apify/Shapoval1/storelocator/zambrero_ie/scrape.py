from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.zambrero.ie"
    api_url = "https://www.zambrero.ie/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[text()="Order & Store Info"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            "".join(tree.xpath("//h2/text()")).replace("\n", "").strip() or "<MISSING>"
        )
        location_name = " ".join(location_name.split())
        ad = (
            "".join(
                tree.xpath('//div[@class="info-inner"]/span[@class="address"]/text()')
            )
            .replace("\n", "")
            .strip()
        )
        postal = "<MISSING>"
        if page_url.find("dundalk") == -1:
            postal = " ".join(ad.split()[-3:-1]).strip()
        try:
            adr = ad.split(f"{postal}")[0].strip()
        except:
            adr = ad
        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or adr
        )
        state = a.state or "<MISSING>"
        country_code = "IE"
        city = a.city or "<MISSING>"
        latitude = "".join(tree.xpath("//span/@data-lat"))
        longitude = "".join(tree.xpath("//span/@data-lng"))
        phone = (
            "".join(
                tree.xpath('//i[@class="fa fa-phone"]/following-sibling::text()[1]')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="hours-item"]/span/text()'))
            .replace("\n", "")
            .strip()
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

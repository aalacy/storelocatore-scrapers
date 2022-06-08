from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.yourfoodtown.com"
    api_url = "https://www.yourfoodtown.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="store-item-box"]')
    for d in div:

        page_url = "".join(d.xpath(".//h4/a/@href"))
        location_name = "".join(d.xpath(".//h4/a/text()"))
        info = d.xpath(".//h4/following-sibling::*//text()")
        info = list(filter(None, [a.strip() for a in info]))
        street_address = "".join(info[0]).strip()
        ad = "".join(info[1]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        phone = "".join(info[2]).strip()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        text = "".join(tree.xpath('//a[contains(text(), "Get Directions")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hooAndPhone = tree.xpath('//div[./div[@class="col"]]//text()')
        hooAndPhone = list(filter(None, [a.strip() for a in hooAndPhone]))
        hours_of_operation = " ".join(hooAndPhone)
        if hours_of_operation.find("Store Phone") != -1:
            hours_of_operation = hours_of_operation.split("Store Phone")[0].strip()
        store_number = page_url.split("-")[-1].replace("/", "").strip()

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
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

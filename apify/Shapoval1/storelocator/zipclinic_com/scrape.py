from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://zipclinic.com/"
    api_url = "https://zipclinic.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="top-menu"]/li[1]//a/following-sibling::ul[1]/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url.count("/") != 6:
            continue
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        info = tree.xpath('//div[./p/a[contains(@href, "tel")]]//text()')
        info = list(filter(None, [a.strip() for a in info]))
        location_name = "".join(info[0]).strip()
        street_address = "".join(info[1]).strip()
        ad = "".join(info[2]).strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
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
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        hours_of_operation = " ".join(info)
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
        if hours_of_operation.find("Open") != -1:
            hours_of_operation = hours_of_operation.split("Open")[1].strip()

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

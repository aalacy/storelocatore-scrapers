from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://paragontheaters.com/"
    api_url = "https://paragontheaters.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="theaterBox"]')
    for d in div:
        slug = "".join(d.xpath("./a/@href"))

        page_url = f"https://paragontheaters.com{slug}"
        location_name = "".join(d.xpath(".//h4//text()")) or "<MISSING>"
        street_address = "".join(d.xpath(".//p/text()[1]")).replace("\n", "").strip()
        ad = "".join(d.xpath(".//p/text()[2]")).replace("\n", "").strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        country_code = "US"
        city = ad.split(",")[0].strip()
        info = d.xpath(".//p//text()")
        info = list(filter(None, [a.strip() for a in info]))
        phone = "<MISSING>"
        if len(info) == 3:
            phone = "".join(info[-1]).strip()
        hours_of_operation = "<MISSING>"
        if page_url.find("COMING") != -1:
            hours_of_operation = "Coming Soon"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ll = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = ll.split("lat=")[1].split("&")[0].strip()
            longitude = ll.split("lon=")[1].split("&")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"

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

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgselenium.sgselenium import SgFirefox


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.bernieandphyls.com/"
    api_url = "https://www.bernieandphyls.com/storelocator.html"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = (
        "".join(tree.xpath('//script[contains(text(), "searchTitleText")]/text()'))
        .split('"markers":')[1]
        .split(',"type":"roadmap"')[0]
        .replace("null", "None")
    )

    js = eval(jsblock)

    for j in js:

        page_url = "".join(j.get("url")).replace("\\", "").strip()
        location_name = "".join(j.get("name"))
        ad = j.get("address")
        a = html.fromstring(ad)
        adr = " ".join(a.xpath("//*//text()")).split("\n")
        adr = list(filter(None, [a.strip() for a in adr]))
        street_address = "".join(adr[0]).strip()
        state = page_url.split("-")[-1].split(".")[0].upper()
        postal = "".join(adr[1]).split(",")[1].strip()
        country_code = "US"
        city = "".join(adr[1]).split(",")[0].strip()
        phone = j.get("contact_phone")
        store_number = j.get("id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        with SgFirefox() as driver:

            driver.get(page_url)
            x = driver.page_source
            tree = html.fromstring(x)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//button[./span[text()="Hours"]]/following-sibling::div[1]//table//tr//td//text()'
                    )
                )
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
                store_number=store_number,
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

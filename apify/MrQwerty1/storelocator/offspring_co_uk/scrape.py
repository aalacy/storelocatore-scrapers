from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='section']")
    cnt = 0

    for d in divs:
        location_name = "".join(d.xpath("./h4/text()")).strip()
        line = d.xpath(".//li/text()")
        phone = SgRecord.MISSING
        if "tel:" in line[-1].lower():
            phone = line.pop().lower().replace("tel:", "").strip()
        if "ext" in phone:
            phone = phone.split("ext")[0].strip()

        if "IRELAND" in line[-1]:
            country_code = "IE"
            line.pop()
            city = line.pop()
            street_address = line.pop()
            postal = SgRecord.MISSING
        else:
            country_code = "GB"
            postal = line.pop()
            city = line.pop()
            street_address = ", ".join(line)

        cnt += 1
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            store_number=cnt,
            phone=phone,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.offspring.co.uk/"
    page_url = "https://www.offspring.co.uk/view/content/storelocator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

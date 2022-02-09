from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sunlife.co.id/id/"
    api_url = "https://www.sunlife.co.id/id/about-us/contact-us/your-nearest-sun-life/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="location"]/option')
    for d in div:
        city = "".join(d.xpath(".//text()"))
        city_value = "".join(d.xpath(".//@value"))
        block = tree.xpath(f'//div[@id="{city_value}"]//div[@class="cmp-text"]')
        for b in block:
            page_url = "https://www.sunlife.co.id/id/about-us/contact-us/your-nearest-sun-life/"
            ad = b.xpath(".//text()")
            ad = list(filter(None, [a.strip() for a in ad]))
            location_name = "".join(ad[0]).strip()
            phone = "<MISSING>"
            phone_list = "".join(ad).replace("\n", "").replace("\xa0", "").strip()
            if phone_list.find("Tel:") != -1:
                phone = phone_list.split("Tel:")[1].strip()
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            if phone.find("DAN") != -1:
                phone = phone.split("DAN")[0].strip()
            if phone.find("Hp.:") != -1:
                phone = phone.split("Hp.:")[0].strip()
            adr = " ".join(ad[1:]).replace("\n", "").replace("\xa0", "").strip()
            if adr.find("Tel") != -1:
                adr = adr.split("Tel")[0].strip()
            a = parse_address(International_Parser(), adr)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "ID"

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
                hours_of_operation=SgRecord.MISSING,
                raw_address=adr,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "www.honda.hr"
    api_url = "http://www.honda.hr/automobili/Dealers.aspx"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@class="CityList"]/option[position()>1]')
    for d in div:

        city = "".join(d.xpath(".//@value"))
        page_url = (
            f"http://www.honda.hr/automobili/DealersList.aspx?ddlCityTitle={city}"
        )
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="dealerResult"]')
        for d in div:

            location_name = "".join(d.xpath(".//h3//text()"))
            location_type = "".join(d.xpath('.//span[@class="title"]/text()'))
            street_address = "".join(
                d.xpath('.//div[@class="dealerAddress"]/p/span[1]/text()')
            )
            ad = (
                "".join(d.xpath('.//div[@class="dealerAddress"]/p/span[2]/text()'))
                .replace("(SPLIT)", "")
                .strip()
            )
            postal = ad.split()[0].strip()
            country_code = "HR"
            ll = "".join(d.xpath(".//iframe/@src"))
            latitude = ll.split("q=")[1].split(",")[0].strip()
            longitude = ll.split("q=")[1].split(",")[1].split("&")[0].strip()
            phone = (
                "".join(d.xpath('.//span[@itemprop="telephone"]/text()')) or "<MISSING>"
            )
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()
            phone = phone.replace("091/", " 091/").replace("01/", " 01/").strip()
            if phone.find(" 0") != -1:
                phone = phone.split(" 0")[0].strip()
            hours_of_operation = (
                " ".join(d.xpath('.//div[@class="dealerColDetails"]//text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = " ".join(hours_of_operation.split())

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=f"{street_address} {ad}",
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_TYPE}
            )
        )
    ) as writer:
        fetch_data(writer)

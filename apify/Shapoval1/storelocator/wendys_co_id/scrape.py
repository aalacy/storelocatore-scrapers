from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "http://www.wendys.co.id"
    api_url = "http://www.wendys.co.id/location/search/R"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.post(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="hasil-search"]/div//span')
    for d in div:
        slug = "".join(d.xpath(".//text()"))

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "multipart/form-data; boundary=---------------------------376098739433867467283407551032",
            "Origin": "http://www.wendys.co.id",
            "Connection": "keep-alive",
            "Referer": "http://www.wendys.co.id/location",
            "Upgrade-Insecure-Requests": "1",
        }
        data = f'-----------------------------376098739433867467283407551032\r\nContent-Disposition: form-data; name="search"\r\n\r\n{slug}\r\n-----------------------------376098739433867467283407551032\r\nContent-Disposition: form-data; name="search_address"\r\n\r\n\r\n-----------------------------376098739433867467283407551032--\r\n'

        r = session.post(
            "http://www.wendys.co.id/location/result_search/",
            headers=headers,
            data=data,
        )
        tree = html.fromstring(r.text)
        div = tree.xpath(
            '//div[@class="col-md-4 col-sm-6 col-xs-12 locations_cont_item"]'
        )
        for d in div:

            page_url = "http://www.wendys.co.id/location/result_search/"
            location_name = "".join(d.xpath(".//h3/text()"))
            ad = (
                "".join(d.xpath('.//label[@class="locations_address"]/text()'))
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "ID"
            city = a.city or "<MISSING>"
            phone = (
                "".join(d.xpath('.//label[contains(text(), "Telp")]/text()'))
                .replace("Telp", "")
                .replace(":", "")
                .strip()
            )

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

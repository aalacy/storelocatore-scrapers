from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.honda-cars.gr"
    api_url = "https://www.honda-cars.gr/dealers/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="darea"]/option[position() > 1]')
    for d in div:
        state = "".join(d.xpath(".//text()"))
        id_state = "".join(d.xpath(".//@value"))
        city_block = d.xpath(f'.//following::select[1]/option[@class="{id_state}"]')
        for c in city_block:

            city = "".join(c.xpath(".//text()"))
            data = {"area": f"{id_state}", "city": f"{city}", "dtype": "dsales"}
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "text/html, */*; q=0.01",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.honda-cars.gr",
                "Connection": "keep-alive",
                "Referer": "https://www.honda-cars.gr/dealers/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers",
            }
            r = session.post(
                "https://www.honda-cars.gr/pages/getDealers.aspx",
                headers=headers,
                data=data,
            )
            try:
                tree = html.fromstring(r.text)
            except:
                continue
            page_url = "https://www.honda-cars.gr/dealers/"
            location_name = "".join(tree.xpath("//h3/text()"))
            location_type = (
                "".join(tree.xpath("//h3/following-sibling::p[1]/text()"))
                .replace("|", ",")
                .replace("\n", "")
                .strip()
            )
            location_type = "".join(location_type[:-1]).strip()
            ad = (
                "".join(tree.xpath("//h3/following-sibling::p[2]/text()"))
                .replace("\n", "")
                .strip()
            )
            street_address = ad.split(",")[0].strip()
            postal = ad.split(",")[-1].strip()
            country_code = "GR"
            phone = (
                "".join(tree.xpath('//p[contains(text(), "Τηλέφωνο")]/text()'))
                .replace("Τηλέφωνο:", "")
                .strip()
            )
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()

            data = {"area": f"{id_state}", "city": f"{city}", "dtype": "dsales"}

            r = session.post(
                "https://www.honda-cars.gr/pages/getDealersMap.aspx",
                headers=headers,
                data=data,
            )
            try:
                latitude = r.text.split("LatLng(")[-1].split(",")[0].strip()
                longitude = (
                    r.text.split("LatLng(")[-1].split(",")[1].split(")")[0].strip()
                )
            except:
                latitude, longitude = "<MISSING>", "<MISSING>"
            if city.find("(") != -1:
                city = city.split("(")[0].strip()

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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=SgRecord.MISSING,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

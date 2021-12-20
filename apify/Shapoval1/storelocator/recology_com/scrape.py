import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.recology.com/"
    api_url = "https://www.recology.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@class="company-select-list"]/li//a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        spage_url = f"https://www.recology.com{slug}"

        session = SgRequests()
        r = session.get(spage_url, headers=headers)
        tree = html.fromstring(r.text)
        slug_page_url = "".join(
            tree.xpath('//a[@class="see-locations-footer-link"]/@href')
        )
        sspage_url = f"https://www.recology.com{slug_page_url}"
        session = SgRequests()
        r = session.get(sspage_url, headers=headers)
        tree = html.fromstring(r.text)

        jsblock = (
            "".join(tree.xpath('//script[contains(text(), "var locations")]/text()'))
            .split("var locations = ")[1]
            .replace(";", "")
            .strip()
        )
        js = json.loads(jsblock)

        for j in js:
            page_url = sspage_url
            location_name = j.get("title")
            location_type = j.get("type")
            if location_type == "OFFIC" or location_type == "OFFI":
                location_type = "Customer Service Offices"
            if location_type == "TRAN":
                location_type = "Transfer Station"
            if location_type == "RECY":
                location_type = "Recylcing Center"
            if location_type == "ORGA":
                location_type = "Compost"
            if location_type == "LAND":
                location_type = "Landfill"
            if location_type == "HAZD":
                location_type = "Household & Hazardous Waste Drop Off"
            if location_type == "STOR":
                location_type = "Store"
            if location_type == "MRF":
                location_type = "Recycling Center"
            street_address = f"{j.get('address_1')} {j.get('address_2')}".strip()
            state = j.get("state")
            postal = j.get("zip")
            country_code = "US"
            city = j.get("city")
            latitude = j.get("lat")
            longitude = j.get("long")
            phone = "".join(j.get("phone")) or "<MISSING>"
            if phone.find("<br>") != -1:
                phone = phone.split("<br>")[0].strip()

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            )
        )
    ) as writer:
        fetch_data(writer)

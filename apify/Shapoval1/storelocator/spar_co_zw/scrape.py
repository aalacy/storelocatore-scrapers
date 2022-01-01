from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.spar.co.zw"
    for i in range(0, 1000):
        api_url = f"https://www.spar.co.zw/stores?pg={i}"
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(api_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//div[@class="listing grid-listing store-listing"]/ul/li')

        for d in div:

            slug = "".join(d.xpath('.//a[contains(@id, "Content_List_Title_")]/@href'))
            page_url = f"https://www.spar.co.zw{slug}"
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            location_name = (
                "".join(tree.xpath("//h2/text()[1]")).replace("\n", "").strip()
            )
            ad = (
                "".join(tree.xpath("//address/text()"))
                .replace(", Click & Collect Pickup", "")
                .replace("\n", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address == "<MISSING>" or street_address == "7099":
                street_address = ad
            state = "".join(tree.xpath("//h2/small/text()"))
            postal = "<MISSING>"
            country_code = "ZW"
            city = a.city or "<MISSING>"
            latitude = (
                "".join(tree.xpath('//script[contains(text(), "lat:")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath('//script[contains(text(), "lat:")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
            if latitude == "0":
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            phone = (
                "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            if phone.find(",") != -1:
                phone = phone.split(",")[0].strip()
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            if phone.find("or") != -1:
                phone = phone.split("or")[0].strip()
            hours_of_operation = (
                " ".join(tree.xpath('//a[@id="Content_WorkingHours"]/text()'))
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            hours_of_operation = hours_of_operation.replace("1600", "16.00")

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
            )

            sgw.write_row(row)
        if len(div) < 9:
            break


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        fetch_data(writer)

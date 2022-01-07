from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://shsalons.com/"
    api_url = "https://shsalons.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//span[text()="SALON LOCATIONS"]/following::ul[1]/li/a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://shsalons.com{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath("//h1/span/text()"))
        info = (
            " ".join(
                tree.xpath(
                    '//span[contains(text(), "Phone:")]/text() | //span[contains(text(), "Add:")]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = info
        if ad.find("Add:") != -1:
            ad = ad.split("Add:")[1].strip()
        if ad.find("Phone:") != -1:
            ad = ad.split("Phone:")[0].strip()
        ad = " ".join(ad.split()[:-3]).replace("(El Dorado Blvd)", "").strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone_list = tree.xpath(
            '//span[contains(text(), "Phone:")]/text() | //span[contains(text(), "Add:")]/text()'
        )
        phone_list = list(filter(None, [a.strip() for a in phone_list]))
        phone = "<MISSING>"
        for p in phone_list:
            if "Phone" in p:
                phone = str(p).replace("Phone:", "").strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[./span[contains(text(), "OPEN HOURS")]]/following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
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
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

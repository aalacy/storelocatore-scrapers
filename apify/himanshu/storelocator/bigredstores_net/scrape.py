import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bigredstores.net/"
    api_url = "https://bigredstores.net/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@id ,"post-")]')
    for d in div:

        page_url = "".join(d.xpath("./a[1]/@href"))
        loc_name = "".join(d.xpath("./h2[1]//text()"))
        cms = "".join(d.xpath('.//*[contains(text(), "Coming Soon")]/text()'))
        a = parse_address(International_Parser(), loc_name)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        store_number = "<MISSING>"
        latitude = "".join(tree.xpath("//div/@data-lat")) or "<MISSING>"
        longitude = "".join(tree.xpath("//div/@data-lng")) or "<MISSING>"
        location_name = "".join(tree.xpath("//div/@data-title")).strip() or "<MISSING>"
        if location_name == "<MISSING>":
            location_name = loc_name
        sub_loc = (
            " ".join(tree.xpath('//div[@class="et_pb_tab_content"]/strong[1]/text()'))
            .replace("\n", "")
            .strip()
        )
        if "Big Red" in sub_loc:
            location_name = sub_loc
        if page_url.find("store155") != -1:
            location_name = "Store #155"
        if location_name.find("Big Red") != -1:
            store_number = location_name.split("Big Red")[1].strip()
        if location_name.find("Store #") != -1:
            store_number = location_name.split("Store #")[1].strip()
        if store_number.find(" ") != -1:
            store_number = store_number.split(" ")[0].strip()
        info = tree.xpath('//div[@class="et_pb_tab_content"]//text()')
        info = list(filter(None, [b.strip() for b in info]))
        info_str = " ".join(info)
        phone_list = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", info_str)
        phone = "<MISSING>"
        if phone_list:
            phone = "".join(phone_list[0]).strip()
        info_1 = tree.xpath(
            '//ul[./li/a[text()="ADDRESS"]]/following-sibling::div[1]//text()'
        )
        add = "<MISSING>"
        if info_1:
            add = (
                "".join(
                    tree.xpath(
                        '//div[@class="et_pb_tab_content"]/strong[1]/following-sibling::text()[2] | //div[@class="et_pb_tab_content"]/h4[./strong][3]//text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        if add != "<MISSING>":
            city = add.split(",")[0].strip()
            state = add.split(",")[1].split()[0].strip()
            postal = add.split(",")[1].split()[1].strip()

        hours_of_operation = "<MISSING>"
        if cms:
            hours_of_operation = "Coming Soon"
        hoo_info = tree.xpath('//div[@class="et_pb_tab_content"]//text()')
        hoo_info = list(filter(None, [b.strip() for b in hoo_info]))
        for i in hoo_info:
            if "24 Hours" in i:
                hours_of_operation = "Open 24 Hours"

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

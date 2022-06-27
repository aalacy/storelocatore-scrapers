import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://curvesvietnam.com.vn"
    api_url = "https://curvesvietnam.com.vn/he-thong-clb/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[contains(@data-name, "custom_html-6")]')
    for b in block:
        name = "".join(b.xpath(".//@data-name"))
        div = b.xpath('.//div[@class="elementor-toggle-item"]')
        for d in div:

            page_url = "https://curvesvietnam.com.vn/he-thong-clb/"
            location_name = "".join(
                d.xpath('.//a[@class="elementor-toggle-title"]/text()')
            )
            ad = (
                " ".join(d.xpath('.//*[contains(text(), "Địa chỉ:")]/text()'))
                .replace("\n", "")
                .replace("Địa chỉ:", "")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "VN"
            js = (
                "".join(
                    d.xpath(
                        'following::script[contains(text(), "fluent_form_ff_form_instance_6_1")]/text()'
                    )
                )
                .split("fluent_form_ff_form_instance_6_1 = ")[1]
                .split(";")[0]
                .strip()
            )
            j = json.loads(js)
            city = (
                j.get("conditionals").get(f"{name}").get("conditions")[0].get("value")
            )
            text = "".join(d.xpath('.//a[contains(@href, "maps")]/@href'))
            try:
                if text.find("ll=") != -1:
                    latitude = text.split("ll=")[1].split(",")[0]
                    longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
                else:
                    latitude = text.split("@")[1].split(",")[0]
                    longitude = text.split("@")[1].split(",")[1]
            except IndexError:
                latitude, longitude = "<MISSING>", "<MISSING>"
            phone = (
                " ".join(d.xpath('.//*[contains(text(), "Điện thoại:")]/text()'))
                .replace("\n", "")
                .replace("Điện thoại:", "")
                .strip()
            )
            if phone.find("/") != -1:
                phone = phone.split("/")[0].strip()
            hours_of_operation = (
                " ".join(d.xpath(".//ul/li//text()")).replace("\n", "").strip()
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
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

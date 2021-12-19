import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mystricklands.com/"
    api_url = "https://www.mystricklands.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[text()="LOCATIONS"]/following::ul[1]/li/a')
    for d in div:
        location_type = SgRecord.MISSING
        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        r = session.get(page_url, headers=headers)
        if "CLOSED FOR THE" in r.text:
            location_type = "Temporarily Closed"
        tree = html.fromstring(r.text)
        cls = "".join(tree.xpath('//img[contains(@src, "Closed")]/@src'))
        if cls:
            continue
        info = (
            " ".join(
                tree.xpath(
                    '//p[@style="font-size:17px"]//text() | //p[@style="text-align:center;font-size:17px"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = info
        if ad.find("Open Daily") != -1:
            ad = ad.split("Open Daily")[0].strip()
        if ad.find("Phone :") != -1:
            ad = ad.split("Phone :")[0].strip()
        if ad.find("pm") != -1:
            ad = (
                ad.split("pm")[1]
                .replace("​ ", "")
                .replace("Liberty Court Plaza", "")
                .strip()
            )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone_list = re.findall(
            re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), info
        )
        phone_list = list(filter(None, [a.strip() for a in phone_list]))
        phone = "".join(phone_list) or "<MISSING>"
        phone = " ".join(phone.split())
        hoo_info = tree.xpath("//p//text()")
        hoo_info = list(filter(None, [a.strip() for a in hoo_info]))
        tmp = []
        for h in hoo_info:
            if "Open" in h or "pm" in h or "Hours" in h or "PM" in h:
                tmp.append(h)

        hours_of_operation = " ".join(tmp).strip() or "<MISSING>"
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
        if hours_of_operation.find("Hours") != -1:
            hours_of_operation = hours_of_operation.split("Hours")[1].strip()

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

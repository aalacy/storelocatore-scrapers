import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://ilfornello.com/"
    api_url = "https://ilfornello.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//ul[@id="primary-menu"]/li[1]//ul/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if page_url == "#":
            continue
        location_name = "".join(d.xpath(".//span/text()")).replace("\n", "").strip()

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = tree.xpath('//a[contains(@href, "goo")]//text()')
        if location_name.find("Bayview") != -1:
            ad = tree.xpath('//a[contains(@href, "goo")]/following::p[1]//text()')

        street_address = "".join(ad[0])
        city = "<MISSING>"
        if street_address.find(",") != -1:
            street_address = "".join(ad[0]).split(",")[0].strip()
            city = "".join(ad[0]).split(",")[1].strip()
        try:
            state = "".join(ad[0]).split(",")[2].split()[0].strip()
            postals = "".join(ad[0]).split(",")[2].split()[1:]
            postal = " ".join(postals)
        except:
            state = "<MISSING>"
            postal = "<MISSING>"
        if city == "<MISSING>":
            city = location_name
        country_code = "CA"
        ad = tree.xpath("//strong//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        adr = " ".join(ad)
        ph = (
            re.findall(
                r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})",
                adr,
            )
            or "<MISSING>"
        )
        phone = "".join(ph[0]).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[.//span[contains(text(), "HOURS")]]/following-sibling::p//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("HOLIDAY HOURS") != -1:
            hours_of_operation = hours_of_operation.split("HOLIDAY HOURS")[0].strip()
        if hours_of_operation.find("Holiday Hours Dec") != -1:
            hours_of_operation = hours_of_operation.split("Holiday Hours Dec")[
                0
            ].strip()
        if hours_of_operation.find("requests.") != -1:
            hours_of_operation = hours_of_operation.split("requests.")[1].strip()
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
        if hours_of_operation.find("Brunch") != -1:
            hours_of_operation = hours_of_operation.split("Brunch")[0].strip()
        if hours_of_operation.find("Phone") != -1:
            hours_of_operation = hours_of_operation.split("Phone")[0].strip()
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        hours_of_operation = (
            hours_of_operation.replace("HOURS OF OPERATION:", "")
            .replace("Open for Indoor Dining", "")
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

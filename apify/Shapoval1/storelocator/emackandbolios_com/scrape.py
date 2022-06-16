import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://emackandbolios.com"
    page_url = "https://emackandbolios.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="elementor-text-editor elementor-clearfix"]/*')
    for d in div:
        info = d.xpath(".//text()")
        info = list(filter(None, [a.strip() for a in info]))
        if not info:
            continue
        location_name = "<MISSING>"
        if len(info) == 4:
            location_name = "".join(info[0]).strip()
        ad = " ".join(info)
        ph = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", ad) or "<MISSING>"
        phone = "".join(ph[0]).replace("<", "").strip() or "<MISSING>"
        if ad.find(f"{phone}") != -1:
            ad = ad.split(f"{phone}")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "Coming Soon":
            continue
        if street_address.find("02-658-1131") != -1:
            street_address = street_address.replace("02-658-1131", "").strip()
            phone = "02-658-1131"
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if postal == "508-945-5506":
            postal = "<MISSING>"
            phone = "508-945-5506"
        country_code = "US"
        if (
            ad.find("Seoul") != -1
            or ad.find("Daejeon") != -1
            or ad.find("Gyeonggi-do") != -1
            or ad.find("Busan") != -1
        ):
            country_code = "Korea"
        if ad.find("Bangkok") != -1 or ad.find("Siam Center 1st Floor") != -1:
            country_code = "Thailand"
        if (
            ad.find("Tsuen Wan") != -1
            or ad.find("Wanchai") != -1
            or ad.find("26 Cochrane Street, Central") != -1
        ):
            country_code = "Hong Kong"
        if (
            ad.find("Ningbo") != -1
            or ad.find("Nanjing") != -1
            or ad.find("Kumming") != -1
            or ad.find("Kumming") != -1
            or ad.find("Taiyuan") != -1
        ):
            country_code = "China"
        if ad.find("Malaysia") != -1 or ad.find("Johor Bahru") != -1:
            country_code = "Malaysia"
        if ad.find("Manila") != -1:
            country_code = "PH"
        if ad.find("Singapore") != -1 or ad.find("West Wing") != -1:
            country_code = "SG"
        city = a.city or "<MISSING>"
        if "Brooklyn" in ad:
            city = "Brooklyn"
        if city == "Las Vegas":
            street_address = "Area 15"
        if street_address == "<MISSING>" and city == "<MISSING>":
            continue
        hours_of_operation = "<MISSING>"
        if city == "Pembroke Pines":
            hours_of_operation = "Coming Soon"
        if ad.find(f"{phone}") != -1:
            ad = ad.replace(f"{phone}", "").strip()
        ad = ad.replace("508-945–5506", "").strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "http://uluke.com"
    page_url = "http://uluke.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="x-acc-content"]/p[.//*[contains(text(), "Phone")]]')
    for d in div:
        inf = d.xpath(".//text()")
        inf = list(filter(None, [a.strip() for a in inf]))
        adr_info = " ".join(inf)
        ad = (
            adr_info.split("|")[1]
            .split("Hours")[0]
            .replace("OPEN 24", "")
            .replace("BP", "")
            .replace("Luke Gas Station", "")
            .strip()
        )
        if ad.find("Phone") != -1:
            ad = ad.split("Phone")[0].strip()
        location_name = "".join(inf[0]).replace("|", "").strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        if "Hobart" in street_address:
            street_address = street_address.replace("Hobart", "").strip()
            city = "Hobart"
        info = " ".join(d.xpath(".//text()")).replace("\n", "").strip()
        store_number = (
            info.split("|")[0].replace("STORE", "").replace("Store", "").strip()
        )
        jsblock = "".join(tree.xpath("//div/@data-x-params"))
        latitude = (
            jsblock.split(f"Store {store_number}")[0]
            .split('"lat":"')[-1]
            .split('"')[0]
            .strip()
        )
        longitude = (
            jsblock.split(f"Store {store_number}")[0]
            .split('"lng":"')[-1]
            .split('"')[0]
            .strip()
        )
        phone = "<MISSING>"
        if info.find("Phone:") != -1:
            phone = info.split("Phone:")[1].replace("Directions", "").strip()
        if phone.find("OPEN") != -1:
            phone = phone.split("OPEN")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath(".//*//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("Luke Gas Station Hours") != -1:
            hours_of_operation = hours_of_operation.split("Luke Gas Station Hours")[
                1
            ].strip()
        if hours_of_operation.find("Luke Car Wash Hours") != -1:
            hours_of_operation = hours_of_operation.split("Luke Car Wash Hours")[
                0
            ].strip()
        if hours_of_operation.find("Hours:") != -1:
            hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
        if (
            hours_of_operation.find("Phone") != -1
            and hours_of_operation.find("OPEN") == -1
        ):
            hours_of_operation = hours_of_operation.split("Phone")[0].strip()
        if hours_of_operation.find("OPEN 24 Hours") != -1:
            hours_of_operation = "OPEN 24 Hours"
        hours_of_operation = (
            hours_of_operation.replace(" | ", " ")
            .replace(":", "")
            .replace("|", "")
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
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)

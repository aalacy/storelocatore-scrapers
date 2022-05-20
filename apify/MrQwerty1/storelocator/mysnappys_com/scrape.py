from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-testid='mesh-container-content']/div[./h6 and .//a]")

    for d in divs:
        index = 0
        line = d.xpath(".//text()")
        line = list(filter(None, [l.replace("\u200b", "").strip() for l in line]))
        for li in line:
            if li == "Get Directions":
                break
            index += 1

        phone = line[index - 1]
        csz = line[index - 2].replace(",", "")
        street_address = line[index - 3]
        location_name = " ".join(line[: index - 3])

        postal = csz.split()[-1]
        state = csz.split()[-2]
        city = csz.replace(postal, "").replace(state, "").strip()
        if "#" in location_name:
            store_number = location_name.split("#")[-1].strip()
        else:
            store_number = SgRecord.MISSING

        location_type = SgRecord.MISSING
        if "coming" in location_name.lower():
            location_type = "Coming Soon"
        text = "".join(d.xpath(".//a[contains(@href, 'maps')]/@href")).replace(
            "%20", ""
        )
        try:
            latitude, longitude = eval(text.split("=")[-1])
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = (
            "".join(line[index:]).split("Hours:")[-1].replace("pm", "pm;").strip()
        )
        if hours_of_operation.endswith(";"):
            hours_of_operation = hours_of_operation[:-1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            store_number=store_number,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.mysnappys.com/"
    page_url = "http://www.mysnappys.com/locations"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.paul-singapore.com/location/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@id, 'row-') and .//h1]")

    for d in divs:
        line = d.xpath(".//text()")
        line = list(filter(None, [l.strip() for l in line]))
        line.pop()
        location_name = line.pop(0)
        raw_address = line.pop(0)
        if "hours" not in line[0]:
            phone = line.pop(0)
        else:
            phone = raw_address.split(")")[-1].strip()
            raw_address = raw_address.replace(phone, "").strip()
        street_address = raw_address.split(", S(")[0]
        postal = raw_address.split(", S(")[-1].replace(")", "")

        if "/" in phone:
            phone = phone.split("/")[0].strip()

        _tmp = []
        for _t in line:
            if "hours" in _t or "Bakery" in _t:
                continue
            _tmp.append(_t)

        hours_of_operation = ";".join(_tmp)
        if "Restaurant" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Restaurant;")[-1].strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            zip_postal=postal,
            country_code="SG",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paul-singapore.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)

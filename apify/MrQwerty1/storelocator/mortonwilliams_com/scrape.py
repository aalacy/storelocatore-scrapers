from itertools import groupby
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = reversed(tree.xpath("//div[@class='_1Q9if']")[2:-2])
    cnt = 0
    c = SgRecord.MISSING

    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(
            filter(
                None,
                [l.replace("\u200b", "").replace("\xa0", "").strip() for l in lines],
            )
        )

        if len(lines) == 1:
            c = lines[0]
            continue

        locations = [
            list(group)
            for k, group in groupby(lines, lambda x: "Manager" in x)
            if not k
        ]

        for loc in locations:
            street_address = loc.pop(0)
            location_name = street_address

            if loc[0].startswith("(") and loc[0].endswith(")"):
                location_name += f" {loc.pop(0)}"

            if "(" in street_address:
                street_address = street_address.split("(")[0].strip()
            if loc[0].startswith("New"):
                csz = loc.pop(0)
                city = csz.split(",")[0].strip()
                csz = csz.split(",")[1].strip()
                state = csz.split()[0]
                postal = csz.split()[-1]
            else:
                city = c
                state = "<MISSING>"
                postal = "<MISSING>"
                if city == "New Jersey":
                    city = "Jersey City"
                    state = c

                if city == "Bronx":
                    cnt += 1
                    if cnt > 1:
                        city = "Manhattan"

            phone = loc.pop(0)
            hours_of_operation = ";".join(loc)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.mortonwilliams.com/"
    page_url = "https://www.mortonwilliams.com/our-locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)

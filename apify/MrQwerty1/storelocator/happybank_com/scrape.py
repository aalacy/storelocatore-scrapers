from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://www.happybank.com/locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'locationCard js-location-card') and not(@data-mb-layer='atm')]"
    )

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[@class='locationCard__heading-text']/text()")
        ).strip()
        page_url = "https://www.happybank.com" + "".join(
            d.xpath(".//a[@class='links__primary--large']/@href")
        )

        line = d.xpath(
            ".//div[@class='locationCard__info-text']/a[contains(@href, 'google')]/text()"
        )
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        try:
            longitude, latitude = "".join(d.xpath("./@data-mb-coords")).split(",")
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        _tmp = []
        li = d.xpath(".//li[@class='locationCard__hours-item']")
        for l in li:
            day = "".join(l.xpath("./span/text()")).strip()
            time = "".join(l.xpath("./strong/text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        row = SgRecord(
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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.happybank.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)

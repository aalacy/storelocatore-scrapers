from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//header[h2[@id='-- NOW OPEN --']]/following-sibling::div[@class='page--store-locations']"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h3[@class='store-name']/text()")).strip()
        line = d.xpath(".//div[@class='page--store-locations--store-info']/p//text()")
        line = list(
            filter(
                None,
                [
                    l.replace("Nanaimo", ",Nanaimo").replace("\xa0", " ").strip()
                    for l in line
                ],
            )
        )

        if "Coming" in line[-1]:
            continue
        if "Shop" in line[-1]:
            line.pop()

        raw_address = ", ".join(line).replace(", 9", "9").replace(",,", ",")
        street_address, city, state, postal = get_international(raw_address)
        if street_address == "3B Hwy":
            street_address = raw_address.split(",")[0].strip()
        country_code = "CA"
        phone = "".join(d.xpath(".//a[@class='store-phone']/text()")).strip()

        text = "".join(d.xpath(".//a[contains(@href, 'google')]/@href"))
        if "/@" in text:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        elif "!3d" in text and "!4d" in text:
            latitude = text.split("!3d")[1].split("!")[0]
            longitude = text.split("!4d")[1]
        else:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        _tmp = []
        days = d.xpath(".//div[@class='page--store-locations--hours-days']/span/text()")
        times = d.xpath(
            ".//div[@class='page--store-locations--hours-time']/span/text()"
        )

        for da, t in zip(days, times):
            _tmp.append(f"{da.strip()}: {t.strip()}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bccannabisstores.com/"
    page_url = "https://www.bccannabisstores.com/pages/store-locations"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

import json
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h[0]
        times = h[1][0]
        line = f"{day} {times}"
        tmp.append(line)
    hours_of_operation = "; ".join(tmp) or "<MISSING>"
    return hours_of_operation


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.pt"
    api_url = "https://www.kfc.pt/a-tua-kfc/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//a[.//strong[text()="- ver no Google"]]')
    for d in div:
        g_url = "".join(d.xpath(".//@href"))

        session = SgRequests()
        r = session.get(g_url, headers=headers)
        tree = html.fromstring(r.text)

        jsblock = (
            "".join(
                tree.xpath(
                    '//script[contains(text(), "APP_INITIALIZATION_STATE")]/text()'
                )
            )
            .split("APP_INITIALIZATION_STATE=")[1]
            .split(";window.APP_FLAGS")[0]
            .strip()
        )
        js = json.loads(jsblock)[3][6]
        js = str(js).split(")]}'")[1].strip()
        js = json.loads(js)

        location_name = js[6][11]
        ad = " ".join(js[6][2]).strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Portugal"
        city = a.city or "<MISSING>"
        latitude = js[6][9][2]
        longitude = js[6][9][3]
        phone = js[6][178][0][0]
        hours = js[6][34][1]
        hours_of_operation = get_hours(hours)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=SgRecord.MISSING,
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)

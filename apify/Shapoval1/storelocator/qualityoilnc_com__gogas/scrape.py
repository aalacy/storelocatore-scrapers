from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://qualityoilnc.com/gogas"
    api_url = "https://qualityplusnc.com/wp-json/wpgmza/v1/datatables/base64eJy1k8FKxDAQht9lzhG2unvJbVEUwcWFFQStyGwy2waTpkzSIpS+u0m3gp682Fvy882XQP4M0NbttcUQQMLz-m73si3LHfIH8YMJ0TRVWW51j40i-YRHSyAgROQIciXAUlPFGuRFIcBh+250shRFYpS3nWuS9HUAjREnvEFHCcgKQlb15JOROxLgWRP-DM4IyAF6tN08x1TRJ8gT2kDjKL7dxYLuywXdVwu61wu6N--vfpvHpsac2zO9qzYpAgwKMvK3SMDJ2EicmrtHRhcy-LubDkPdtfc3uZ3JqTBS5dlQ3sMGctSF6N2tIasnKFl9T8xG0-wrHvNdDxTzOsxnJ7PR6timzqzHLw2eHDA/eJwTZ2BgYFnAAAcKQMz+--8HBgYAHRkD0Q"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    for j in js:

        page_url = "https://qualityplusnc.com/stations-locations-all/"
        location_name = "".join(j[1])
        location_type = "".join(j[2])
        ad = "".join(j[3])
        a = parse_address(USA_Best_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        store_number = "<MISSING>"
        if location_name.find("#") != -1:
            store_number = location_name.split("#")[1].strip()
        info = "".join(j[4])
        i = html.fromstring(info)
        phone = "".join(i.xpath("//p[1]/text()")) or "<MISSING>"

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
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

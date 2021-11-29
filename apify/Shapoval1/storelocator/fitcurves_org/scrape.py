from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://fitcurves.org/"
    api_url = "https://fitcurves.org/clubs/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//select[@id="country"]/option[position() > 1]')
    for d in div:
        slug = "".join(d.xpath(".//text()"))
        r = session.get(
            f"https://fitcurves.org/wp-admin/admin-ajax.php?action=pageData&country={slug}&city=&district=&metro="
        )
        js = r.json()
        for j in js:
            city_url = j.get("city_url")
            id_s = j.get("id")
            page_url = f"https://fitcurves.org/clubs/page_{city_url}_{id_s}/"
            location_name = j.get("name") or "<MISSING>"
            street_address = j.get("address") or "<MISSING>"
            state = j.get("region") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            phone = j.get("phone_1") or "<MISSING>"
            days = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            tmp = []
            for d in days:
                day = d
                time = j.get(f"shed_{d}") or "<MISSING>"
                line = f"{day} {time}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp) or "<MISSING>"
            if hours_of_operation.count("<MISSING>") > 5:
                hours_of_operation = "<MISSING>"

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=SgRecord.MISSING,
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        fetch_data(writer)

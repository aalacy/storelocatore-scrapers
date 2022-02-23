from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.pasticceriamarchesi.com"
    api_url = "https://www.pasticceriamarchesi.com/ww/en/shops.msi.getShopStores.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    js = r.json()
    for j in js.values():
        if str(j) == "True":
            continue
        for a in j:

            page_url = "https://www.pasticceriamarchesi.com/en/shops.html"
            location_name = a.get("short_name")
            location_type = a.get("type")
            street_address = a.get("address")[0]
            ad = "".join(a.get("address")[1]).replace("London,", "London")
            phone = a.get("phone")
            postal = ad.split()[0].strip()
            city = ad.split()[1].strip()
            country_code = a.get("countryGroup")
            hours_of_operation = (
                "".join(a.get("hours")).replace("/", "").replace("\r\n", "").strip()
            )
            latitude = a.get("map")[0].get("lat")
            longitude = a.get("map")[0].get("lng")

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

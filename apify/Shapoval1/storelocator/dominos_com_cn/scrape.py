from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dominos.com.cn/"
    api_url = "https://m8api.dominos.com.cn/dominos/menu/o-s-ms/misc.service/getAllCity?ver=0.35068153664572&deviceid=a3eb85bbb5f766ee8e04de82958867c0&devicetype=wap&channelId=1&isStoreCode=false&channelCode=WAP"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]
    for j in js:

        city_code = j.get("cityCode")
        city = j.get("cityNameEN")
        r = session.get(
            f"https://m8api.dominos.com.cn/dominos/menu/o-s-ms/misc.service/getStoreListByDistrict?ver=0.6878353552690912&deviceid=a3eb85bbb5f766ee8e04de82958867c0&devicetype=wap&cityCode={city_code}&channelId=1&isStoreCode=true&channelCode=WAP"
        )
        js = r.json()["data"]
        for j in js:

            page_url = "https://dominos.com.cn/selectAddress"
            location_name = j.get("storeName")
            ad = (
                str(j.get("storeAddressEN"))
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("None", "<MISSING>")
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            state = j.get("districtNameCN") or "<MISSING>"
            postal = j.get("cityCode") or "<MISSING>"
            country_code = "CN"
            phone = j.get("storeTel") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("lng") or "<MISSING>"
            store_number = j.get("storeCode") or "<MISSING>"
            hours_of_operation = "<MISSING>"
            if street_address == "Opening Soon":
                street_address = "<MISSING>"
                hours_of_operation = "Coming Soon"
            status = j.get("status")
            if status == 0:
                hours_of_operation = "Temporary closed"

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
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)

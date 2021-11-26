from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.skechers.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://hosted.where2getit.com",
        "Connection": "keep-alive",
        "Referer": "https://hosted.where2getit.com/skechers/index.html",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    data = '{"request":{"appkey":"8C3F989C-6D95-11E1-9DE0-BB3690553863","formdata":{"objectname":"Account::Country"}}}'

    r = session.post(
        "https://hosted.where2getit.com/skechers/rest/getlist?lang=en_US&like=0.3279255172998665",
        headers=headers,
        data=data,
    )
    js = r.json()["response"]["collection"]
    for j in js:
        slug = j.get("name")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://hosted.where2getit.com",
            "Connection": "keep-alive",
            "Referer": "https://hosted.where2getit.com/skechers/index.html",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data = (
            '{"request":{"appkey":"8C3F989C-6D95-11E1-9DE0-BB3690553863","formdata":{"order":"rank::numeric","limit":10000,"objectname":"Locator::Store","where":{"country":{"eq":"'
            + slug
            + '"},"expdate":{"ge":"2021-109"}, "authorized":{"distinctfrom":"1"},"or":{"retail":{"eq":""},"outlet":{"eq":""},"warehouse":{"eq":""},"apparel_store":{"eq":""},"curbside_pickup":{"eq":""},"reduced_hours":{"eq":""},"in_store_pickup":{"eq":""},"promotions":{"eq":""}}}}}}'
        )

        r = session.post(
            "https://hosted.where2getit.com/skechers/rest/getlist?like=0.16207988000569884&lang=en_US",
            headers=headers,
            data=data,
        )
        try:
            js = r.json()["response"]["collection"]
        except:
            js = []
        for j in js:
            page_url = "https://www.skechers.com/store-locator.html"
            location_name = j.get("name") or "<MISSING>"

            street_address = (
                f"{j.get('address1')} {j.get('address2')}".replace("None", "")
                .replace("\n", "")
                .strip()
                or "<MISSING>"
            )
            state = j.get("state") or j.get("province") or "<MISSING>"
            state = str(state).replace("&#xf1;", "ñ").strip()
            if state == "110001":
                state = "<MISSING>"
            postal = j.get("postalcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            store_number = j.get("storeid") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            if latitude == "<MISSING>":
                continue
            longitude = j.get("longitude") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            hours_of_operation = (
                f"Mon {j.get('rmon')} Tue {j.get('rtues')} Wed {j.get('rwed')} Thur {j.get('rthurs')} Fri {j.get('rfri')} Sat {j.get('rsat')} Sun {j.get('rsun')}"
                or "<MISSING>"
            )
            if hours_of_operation.count("None") == 7:
                hours_of_operation = "<MISSING>"
            if (
                hours_of_operation.count("CLOSED") == 7
                or hours_of_operation.count("Closed") == 7
            ):
                hours_of_operation = "Closed"

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
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LOCATION_NAME,
                }
            )
        )
    ) as writer:
        fetch_data(writer)

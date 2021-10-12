from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch
from concurrent import futures


def get_data(zips, sgw: SgWriter, slug):

    locator_domain = "https://www.skechers.com/"
    api_url = "https://hosted.where2getit.com/skechers/rest/locatorsearch?like=0.8255307432519684&lang=en_US"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }
    data = (
        '{"request":{"appkey":"8C3F989C-6D95-11E1-9DE0-BB3690553863","formdata":{"geoip":false,"dataview":"store_default","order":"_distance","limit":100,"geolocs":{"geoloc":[{"addressline":"'
        + str(zips)
        + '","country":"'
        + str(slug).upper()
        + '"}]},"searchradius":"250","where":{"expdate":{"ge":"2021-912"},"authorized":{"distinctfrom":"1"},"or":{"retail":{"eq":""},"outlet":{"eq":""},"warehouse":{"eq":""},"apparel_store":{"eq":""},"curbside_pickup":{"eq":""},"reduced_hours":{"eq":""},"in_store_pickup":{"eq":""},"promotions":{"eq":""}}},"false":"0"}}}'
    )
    print(data)
    session = SgRequests()

    r = session.post(api_url, headers=headers, data=data)
    try:
        js = r.json()["response"]["collection"]
    except:
        return
    for j in js:
        page_url = "https://www.skechers.com/store-locator.html"
        location_name = "Skechers"
        street_address = (
            f"{j.get('address1')} {j.get('address2')}".replace("None", "")
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        state = j.get("state") or j.get("province") or "<MISSING>"
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


def fetch_data(sgw: SgWriter):

    session = SgRequests()
    data = '{"request":{"appkey":"8C3F989C-6D95-11E1-9DE0-BB3690553863","formdata":{"objectname":"Account::Country"}}}'
    r = session.post(
        "https://hosted.where2getit.com/skechers/rest/getlist?lang=en_US&like=0.04642551284402763",
        data=data,
    )
    js = r.json()["response"]["collection"]
    for j in js:
        slug = "".join(j.get("name"))
        zips = DynamicZipSearch(
            country_codes=[f"{slug}".lower()], max_search_distance_miles=10
        )

        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(get_data, url, sgw, slug): url for url in zips
            }
            for future in futures.as_completed(future_to_url):
                future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)

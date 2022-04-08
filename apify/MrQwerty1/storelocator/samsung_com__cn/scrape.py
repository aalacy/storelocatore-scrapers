import json5
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_params():
    urls = []
    new_js = dict()
    r = session.get(
        "https://support-cn.samsung.com.cn/samsung-experience-store/locations/data/js/zh-cn_region",
        headers=headers,
    )
    text = r.text.split("=")[-1].replace(";", "")
    js = json5.loads(text)["regions"]

    for k, v in js.items():
        p = v.get("p")
        if not p or p == "0":
            url = f"https://support-cn.samsung.com.cn/samsung-experience-store/locations/store/AjaxDataList?pro={k}&region=0&lng=&lat=&types=1"
            urls.append(url)

        if " " in k:
            k = k.strip()

        new_js[k] = v

    return urls, new_js


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()

    return street


def fetch_data(sgw: SgWriter):
    apis, params = get_params()
    for api in apis:
        r = session.get(api, headers=headers)
        js = r.json()["Items"]

        for j in js:
            raw_address = j.get("address")
            state_key = str(j.get("province"))
            state = params[state_key]["t"]
            city_key = str(j.get("region"))
            city = params[city_key]["t"]
            street_address = get_international(raw_address)
            postal = j.get("zipcode")
            country_code = "CN"
            store_number = j.get("storeID")
            location_name = j.get("name")
            location_type = j.get("locationType")
            phone = j.get("tel")
            latitude = j.get("latitude")
            longitude = j.get("longitude")

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
                location_type=location_type,
                phone=phone,
                store_number=store_number,
                locator_domain=locator_domain,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.samsung.com/cn/"
    page_url = "https://support-cn.samsung.com.cn/samsung-experience-store/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

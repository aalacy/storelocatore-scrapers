from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.haidilao.com"
base_url = "https://www.haidilao.com/cn/eportal/store/listObjByPosition?longitude=-95.712891&latitude=37.09024&mapType=0&country=CN&language=zh"
sg_url = "https://www.haidilao.com/sg/eportal/store/listObjByPosition?longitude=-118.3887&latitude=33.956&mapType=0&country=SG&language=en"


def _d(_, page_url, street_address, city, state, zip_postal=None):
    phone = _["storeTelephone"]
    if phone:
        phone = phone.split(",")[0].replace("022-69198883", "").strip()
    hours_of_operation = _["openTime"]
    if "暂停营业" in hours_of_operation:
        hours_of_operation = ""
    return SgRecord(
        page_url=page_url,
        location_name=_["storeName"],
        street_address=street_address,
        city=city.replace("SM", ""),
        state=state,
        zip_postal=zip_postal,
        latitude=_["latitude"],
        longitude=_["longitude"],
        country_code=_["countryId"],
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=_["storeAddress"].replace("\n", ""),
    )


def fetch_data():
    with SgRequests() as session:
        locations = session.get(base_url, headers=_headers).json()["value"]
        for _ in locations:
            raw_address = _["storeAddress"].replace("地址:", "").replace("\n", "")
            raw_address = raw_address.replace("中国", "")
            state = city = ""
            if "澳门" in raw_address:
                city = "澳门"
                street_address = raw_address.replace("澳门", "")
            if "香港" in raw_address:
                city = "香港"
                street_address = raw_address.replace("香港", "")
            if "省" in raw_address:
                state = raw_address.split("省")[0] + "省"
                raw_address = raw_address.split("省")[-1]
            if "自治区" in raw_address:
                state = raw_address.split("自治区")[0] + "自治区"
                raw_address = raw_address.split("自治区")[-1]
            if "内蒙古" in raw_address:
                state = "内蒙古"
                raw_address = raw_address.replace("内蒙古", "")
            if "自治州" in raw_address:
                state = raw_address.split("自治州")[0] + "自治州"
                raw_address = raw_address.split("自治州")[-1]

            if "路" in city:
                _cc = city.split("路")
                city = _cc[-1]
                street_address = _cc[0] + "路" + street_address
            if "号" in city:
                _cc = city.split("号")
                city = _cc[-1]
                street_address = _cc[0] + "号" + street_address
            if "区" in city:
                _cc = city.split("区")
                city = _cc[-1]
                street_address = _cc[0] + "区" + street_address

            if "市" in raw_address:
                _ss = raw_address.split("市")
                street_address = _ss[-1]
                city = _ss[0]
                if "市" not in city:
                    city += "市"

            yield _d(
                _,
                "https://www.haidilao.com/cn/serve/storeSearch",
                street_address,
                city,
                state,
            )

        locations = session.get(sg_url, headers=_headers).json()["value"]
        for _ in locations:
            raw_address = _["storeAddress"].replace("\n", "").replace("，", ",")
            state = city = ""
            addr = raw_address.split(",")
            city = addr[-1].strip().split()[0]
            zip_postal = addr[-1].strip().split()[-1]
            street_address = ", ".join(addr[:-1])

            yield _d(
                _,
                "https://www.haidilao.com/sg/serve/storeSearch",
                street_address,
                city,
                state,
                zip_postal,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

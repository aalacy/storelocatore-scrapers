from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.thenorthface.com.cn"
base_url = "https://www.thenorthface.com.cn/index.php/article-cominfo_contact-272.html?_t=b25eea2a28b11807ce25664c70041bcc"


def fetch_data():
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        locations = soup.select("div.article-content table tr")[1:]
        for _ in locations:
            td = _.select("td")
            raw_address = td[-1].text.strip().replace("中国", "")
            state = street_address = city = ""
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
            if not street_address:
                street_address = raw_address.replace(td[0].text.strip(), "")

            yield SgRecord(
                page_url=base_url,
                location_name=td[1].text.strip(),
                street_address=street_address,
                city=td[0].text.strip() or city,
                state=state,
                country_code="CN",
                phone=td[2].text.strip(),
                locator_domain=locator_domain,
                raw_address=raw_address,
            )


if __name__ == "__main__":
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

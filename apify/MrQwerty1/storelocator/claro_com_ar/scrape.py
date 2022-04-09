import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
    _types = ["AMBA", "Interior del país"]

    cnt = 0
    for location_type in _types:
        js = json.loads(text)["props"]["pageProps"]["fields"]["content"][2]["fields"][
            "content"
        ][cnt]["fields"]["content"][0]["fields"]["content"]

        for j in js:
            j = j["fields"]
            location_name = j.get("title")
            street_address = j.get("text")
            state = j.get("category")
            country_code = "AR"

            _tmp = []
            hours = j.get("bullets") or []
            for h in hours:
                t = h["fields"]["text"] or ""
                if ".com" in t:
                    continue
                _tmp.append(t)

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                state=state,
                location_type=location_type,
                country_code=country_code,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)

        cnt += 1


if __name__ == "__main__":
    locator_domain = "https://www.claro.com.ar/"
    page_url = "https://www.claro.com.ar/personas/sucursales"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

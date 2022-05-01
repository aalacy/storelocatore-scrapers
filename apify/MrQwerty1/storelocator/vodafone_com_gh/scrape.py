from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def get_params():
    out = dict()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    option = tree.xpath("//select[@id='selectedRegion']/option")
    option.pop(0)

    for o in option:
        key = "".join(o.xpath("./@value"))
        val = "".join(o.xpath("./text()"))
        out[key] = val

    return out


def fetch_data(sgw: SgWriter):
    params = get_params()
    api = "https://myvodafone.vodafone.com.gh/digicare-get-retail-shops"
    for i, state in params.items():
        json_data = {"regionID": str(i)}
        r = session.post(api, headers=headers, json=json_data)
        js = r.json()

        for j in js:
            location_name = j.get("location")
            street_address = j.get("landmark")
            hours_of_operation = j.get("opening_hours") or ""
            hours_of_operation = (
                hours_of_operation.replace("\r\n", "")
                .replace(" <br/> ", ";")
                .replace("<br/>", ";")
            )
            postcode = j.get("ghana_post")
            text = j.get("gps") or ""
            try:
                latitude, longitude = text.split(",")
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                state=state,
                zip_postal=postcode,
                latitude=latitude,
                longitude=longitude,
                country_code="GH",
                hours_of_operation=hours_of_operation,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://vodafone.com.gh/"
    page_url = "https://support.vodafone.com.gh/help/retailshop/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
        "Accept": "*/*",
        "Referer": "https://support.vodafone.com.gh/",
        "Origin": "https://support.vodafone.com.gh",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }

    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)

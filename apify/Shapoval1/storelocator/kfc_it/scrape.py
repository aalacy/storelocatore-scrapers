import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.kfc.it/"
    api_url = "https://www.kfc.it/ristoranti"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(
        tree.xpath('//script[contains(text(), "initialReduxState")]/text()')
    ).strip()
    js = json.loads(jsblock)
    for j in js["props"]["initialProps"]["pageProps"]["pageBlocks"][0]["block"][
        "items"
    ]:
        slug = j.get("internal_code")
        page_url = f"https://www.kfc.it/ristoranti?s={slug}"
        location_name = j.get("name")
        street_address = f"{j.get('address_1')} {j.get('address_2')}".strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "IT"
        city = j.get("city")
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours = j.get("hours")
        hours_of_operation = "<MISSING>"
        tmp = []
        if hours:
            hours_lst = eval(hours)
            for h in hours_lst:
                day = h.get("day")
                times = h.get("hour")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = (
                "; ".join(tmp)
                .replace("Consumo al ristorante", "")
                .replace(
                    "Salvo diverse disposizioni delle autorità nazionali e locali.", ""
                )
                .strip()
            )
        if hours_of_operation.find("Delivery") != -1:
            hours_of_operation = hours_of_operation.split("Delivery")[0].strip()
        if hours_of_operation.endswith(";"):
            hours_of_operation = "".join(hours_of_operation[:-1])
        if hours_of_operation.find("; Asporto") != -1:
            hours_of_operation = hours_of_operation.split("; Asporto")[0].strip()

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

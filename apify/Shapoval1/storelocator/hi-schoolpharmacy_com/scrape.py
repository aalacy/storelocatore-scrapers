from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://locations.myhspstores.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locations.myhspstores.com/?location=103%20Robbins%20St%20&category=10&radius=100",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://locations.myhspstores.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    data = {"action": "get_all_stores", "lat": "", "lng": ""}

    r = session.post(
        "https://locations.myhspstores.com/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js.values():
        location_name = "".join(j.get("na"))
        if (
            location_name.find("Pharmacy") == -1
            and location_name.find("Hi-School") == -1
        ):
            continue
        street_address = j.get("st")
        phone = j.get("te") or "<MISSING>"
        city = "".join(j.get("ct")).strip()
        if city.find(",") != -1:
            city = city.split(",")[0]
        try:
            state = location_name.split(",")[1].strip()
        except:
            state = "<MISSING>"

        country_code = "US"
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = "<MISSING>"

        page_url = "".join(j.get("gu"))
        if hours_of_operation == "<MISSING>":
            session = SgRequests()
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//div[@class="et_pb_text_inner"]/p[./strong[contains(text(), "Hours")]][1]//text()'
                    )
                )
                .replace("\n", " ")
                .strip()
                or "<MISSING>"
            )
            if hours_of_operation == "<MISSING>":
                hours_of_operation = (
                    " ".join(
                        tree.xpath(
                            '//div[@class="et_pb_text_inner"]/p[./b[contains(text(), "Hours")]][1]//text()'
                        )
                    )
                    or "<MISSING>"
                )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"
            if hours_of_operation.find("Hours:") != -1:
                hours_of_operation = hours_of_operation.split("Hours:")[1].strip()
        postal = j.get("zp") or "<MISSING>"

        if state == "<MISSING>":
            session = SgRequests()
            r = session.get(page_url)
            tree = html.fromstring(r.text)
            ad = (
                "".join(
                    tree.xpath(
                        '//div[@class="store_locator_single_address"]/text()[last()]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
            state = ad.split(",")[1].split()[0].strip()
            if phone == "<MISSING>":
                phone = (
                    "".join(tree.xpath('//span[@role="link"]/text()')) or "<MISSING>"
                )

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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

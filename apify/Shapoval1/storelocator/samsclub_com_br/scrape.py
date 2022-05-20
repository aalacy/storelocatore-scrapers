from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://samsclub.com.br/"
    r = session.get("https://sejasocio.samsclub.com.br/#encontre-um-clube")
    tree = html.fromstring(r.text)
    nonce_state = "".join(tree.xpath("//section/@data-nonce-states"))
    nonce_cities = "".join(tree.xpath("//section/@data-nonce-cities"))
    nonce_clubs = "".join(tree.xpath("//section/@data-nonce-clubs"))

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://sejasocio.samsclub.com.br/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }
    r = session.get(
        f"https://sejasocio.samsclub.com.br/wp-admin/admin-ajax.php?action=get_clubs_states&nonce={nonce_state}",
        headers=headers,
    )
    js = r.json()["data"]
    for j in js:
        state = j
        r = session.get(
            f"https://sejasocio.samsclub.com.br/wp-admin/admin-ajax.php?action=get_clubs_cities&state={state}&nonce={nonce_cities}"
        )
        js = r.json()
        for j in js["data"]:
            city = j
            r = session.get(
                f"https://sejasocio.samsclub.com.br/wp-admin/admin-ajax.php?action=get_clubs&state={state}&city={city}&nonce={nonce_clubs}",
                headers=headers,
            )
            js = r.json()["data"]
            for j in js:

                page_url = "https://sejasocio.samsclub.com.br/"
                location_name = (
                    "".join(j.get("name")).replace("&#8217;", "`") or "<MISSING>"
                )
                ad = j.get("address")
                a = parse_address(International_Parser(), ad)
                street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                    "None", ""
                ).strip()
                postal = a.postcode or "<MISSING>"
                country_code = "Brazil"
                if location_name.find("Sam's Club ") != -1:
                    city = location_name.replace("Sam's Club ", "").strip()
                phone = j.get("phones") or "<MISSING>"
                if "<br />" in phone:
                    phone = str(phone).split("\n")[0].replace("<br />", "").strip()
                hours_of_operation = f"Weekdays {j.get('hours_week')} Saturday {j.get('hours_saturday')} Sunday {j.get('hours_sunday')}"
                if hours_of_operation == "Weekdays   Saturday   Sunday  ":
                    hours_of_operation = "<MISSING>"
                if hours_of_operation == "<MISSING>":
                    hours_of_operation = j.get("hours_note") or "<MISSING>"

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
                    latitude=SgRecord.MISSING,
                    longitude=SgRecord.MISSING,
                    hours_of_operation=hours_of_operation,
                    raw_address=ad,
                )

                sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests(verify_ssl=False)
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)

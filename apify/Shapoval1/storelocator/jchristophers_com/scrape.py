from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address

locator_domain = "https://jchristophers.com/"


def fetch_data(sgw: SgWriter):

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://jchristophers.com",
        "Connection": "keep-alive",
        "Referer": "https://jchristophers.com/locations/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    data = {"action": "get_all_stores", "lat": "", "lng": ""}

    r = session.get("https://jchristophers.com/locations/", headers=headers, data=data)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@id="select-by-name"]//a')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"https://jchristophers.com{slug}"
        page_url_slug = page_url.split("/")[-1].strip()
        try:
            r = SgRequests.raise_on_err(session.get(page_url, headers=headers))
        except:
            r = SgRequests.raise_on_err(
                session.get("https://jchristophers.com/locations/", headers=headers)
            )
        tree = html.fromstring(r.text)
        location_name = "".join(tree.xpath("//h1/text()")) or "<MISSING>"
        ad = (
            " ".join(tree.xpath("//h1/following-sibling::p[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        city = a.city or "<MISSING>"
        country_code = "US"
        map_link = "".join(tree.xpath("//iframe/@src"))
        try:
            latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
            longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            "".join(tree.xpath('//p[contains(text(), "Serving Daily:")]/text()'))
            .replace("Serving", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            r = session.get("https://jchristophers.com/locations/", headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h3[text()="Hours of Operation"]/following-sibling::p[position()<3]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()')) or "<MISSING>"
        if page_url == "https://jchristophers.com/locations/canton":
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://jchristophers.com",
                "Connection": "keep-alive",
                "Referer": "https://jchristophers.com/locations/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
            data = {"action": "get_all_stores", "lat": "", "lng": ""}

            r = session.post(
                "https://jchristophers.com/wp-admin/admin-ajax.php",
                headers=headers,
                data=data,
            )
            js = r.json()
            for j in js.values():
                url = "".join(j.get("gu")) or "<MISSING>"
                if url[-1] == "/":
                    url = "".join(url[:-1])
                url_slug = url.split("/")[-1].strip()
                if page_url_slug == url_slug:
                    location_name = j.get("na") or "<MISSING>"
                    street_address = j.get("st") or "<MISSING>"
                    postal = j.get("zp") or "<MISSING>"
                    country_code = "US"
                    latitude = j.get("lat") or "<MISSING>"
                    longitude = j.get("lng") or "<MISSING>"
                    phone = j.get("te") or "<MISSING>"
                    city = location_name
                    state = "<MISSING>"
                    if city == "Canton":
                        state = "Ohio"

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

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://clubchampiongolf.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "If-Modified-Since": "Wed, 13 Oct 2021 19:00:21 GMT",
        "Cache-Control": "max-age=0",
    }
    data = {
        "searchname": "",
        "filter_catid": "",
        "searchzip": "Please enter your zip code (i.e. 60527)",
        "task": "search",
        "qradius": "9",
        "radius": "-1",
        "option": "com_mymaplocations",
        "limit": "0",
        "component": "com_mymaplocations",
        "Itemid": "102",
        "zoom": "10",
        "format": "json",
        "geo": "",
        "latitude": "",
        "longitude": "",
        "limitstart": "0",
    }

    r = session.post(
        "https://clubchampiongolf.com/locations", headers=headers, data=data
    )
    if r.status_code != 200:
        return
    js = r.json()["features"]
    for j in js:

        slug = (
            "".join(j.get("properties").get("url"))
            .replace(".", "")
            .replace("fcom", "f.com")
            .strip()
        )

        page_url = slug
        if page_url.find("https") == -1:
            page_url = f"https://clubchampiongolf.com{slug}"
        sub_ad = ""
        if slug.find("txgca") != -1:
            page_url = "https://clubchampiongolf.com/locations"
            info = j.get("properties").get("description")
            n = html.fromstring(info)
            sub_ad = (
                " ".join(n.xpath('//a[contains(@title, "TXG")]/text()'))
                .replace("\n", "")
                .strip()
            )
            sub_ad = " ".join(sub_ad.split())
        location_name = j.get("properties").get("name")
        store_number = j.get("id")
        latitude = j.get("geometry").get("coordinates")[1]
        longitude = j.get("geometry").get("coordinates")[0]

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//td[.//img[contains(@src, "find")]]/following-sibling::td//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        if page_url == "https://clubchampiongolf.com/locations":
            ad = sub_ad
        ad = ad.replace("Our new location is:", "").strip()
        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        if not postal.isdigit():
            country_code = "CA"
        city = a.city or "<MISSING>"
        if ad.find(", ON") != -1:
            state = ad.split(",")[-1].split()[0].strip()
            postal = " ".join(ad.split(",")[-1].split()[1:]).strip()
        phone = (
            "".join(
                tree.xpath('//tbody//td[2]//a[contains(@href, "tel")]/text()')
            ).strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(
                    tree.xpath(
                        '//td[.//img[contains(@src, "call")]]/following-sibling::td//p/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    "//div[./h3]/following-sibling::div[1]//*[contains(text(), ':')]/text()"
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if hours_of_operation.find("GET") != -1:
            hours_of_operation = hours_of_operation.split("GET")[0].strip()
        if hours_of_operation.find("Get") != -1:
            hours_of_operation = hours_of_operation.split("Get")[0].strip()
        cms = "".join(tree.xpath('//span[text()="Coming Soon!"]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"

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
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.luluhypermarket.com/en-ae/"
    api_url = "https://www.luluhypermarket.com/en-ae/store-finder"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="dropdown-menu country-dropdown "]/a')
    for d in div:
        country_code = "".join(d.xpath(".//@data-isocode")).upper()
        slug_url = "".join(d.xpath(".//@data-url"))
        country_slug = slug_url.split("store-finder")[0].strip()

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Referer": f"https://www.luluhypermarket.com{country_slug}store-finder",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        country_url = f"https://www.luluhypermarket.com{slug_url}"
        r = session.get(country_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//select[@id="storelocator-query"]/option[position()>1]')[:1]
        for d in div:
            city_slug = "".join(d.xpath(".//@value"))
            api_url = f"https://www.luluhypermarket.com{country_slug}store-finder?q={city_slug}&page=0"
            r = session.get(api_url, headers=headers)
            try:
                js = r.json()
            except:
                continue
            total = js.get("total")
            for i in range(0, int(total / 10 + 1)):
                r = session.get(
                    f"https://www.luluhypermarket.com{country_slug}store-finder?q={city_slug}&page={i}"
                )
                try:
                    js = r.json()["data"]
                except:
                    continue
                for j in js:
                    page_url = (
                        f"https://www.luluhypermarket.com{country_slug}store-finder"
                    )
                    location_name = j.get("displayName") or "<MISSING>"
                    location_name = str(location_name).replace("&amp;", "&").strip()
                    ad = f"{j.get('line1')} {j.get('line2')}".replace(
                        "None", ""
                    ).strip()
                    a = parse_address(International_Parser(), ad)
                    street_address = (
                        f"{a.street_address_1} {a.street_address_2}".replace(
                            "None", ""
                        ).strip()
                        or "<MISSING>"
                    )
                    if street_address == "<MISSING>" or street_address.isdigit():
                        street_address = ad
                    postal = j.get("postalCode") or "<MISSING>"
                    store_number = j.get("name")
                    latitude = j.get("latitude") or "<MISSING>"
                    longitude = j.get("longitude") or "<MISSING>"
                    phone = (
                        "".join(j.get("phone"))
                        .replace("Tel:", "")
                        .replace("Phone:", "")
                        .strip()
                        or "<MISSING>"
                    )
                    location_type = "<MISSING>"
                    features = j.get("features")
                    if features:
                        location_type = ",".join(features)
                    city = j.get("town") or "<MISSING>"
                    city = (
                        str(city)
                        .replace("56100", "")
                        .replace("40170", "")
                        .replace("1", "")
                        .replace("3", "")
                        .replace("5", "")
                        .replace(", Al Mabelah", "")
                        .replace("(SOHAR)", "")
                        .replace("51", "")
                        .strip()
                        or "<MISSING>"
                    )
                    postal = str(postal).replace("_MY-WP-KUL", "").strip()

                    row = SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=SgRecord.MISSING,
                        zip_postal=postal,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=SgRecord.MISSING,
                    )

                    sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        fetch_data(writer)

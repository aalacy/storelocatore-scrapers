import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_urls():
    urls = []
    start_urls = [
        "https://decathlon.com.au/pages/store-locator",
        "https://decathlon.lk/pages/store-locator",
    ]

    for url in start_urls:
        r = session.get(url, headers=headers)
        tree = html.fromstring(r.text)
        script = "".join(tree.xpath("//script[contains(text(), 'var urls =')]/text()"))
        script = script.split("var urls =")[1].split("];")[0].replace("\\", "") + "]"
        links = eval(script)

        for link in links:
            if "sca.storelocator_scripttag.js" in link:
                urls.append(link)
                break

    return urls


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    for api in urls:
        r = session.get(api, headers=headers)
        text = (
            r.text.split('"locationsRaw":"')[1]
            .split('}]"')[0]
            .replace("\\r", "")
            .replace("\\", "")
            .replace('""', '"')
            + "}]"
        )
        js = json.loads(text)

        for j in js:
            if "australia" in api:
                locator_domain = "https://decathlon.com.au/"
                page_url = (
                    j.get("web") or "https://decathlon.com.au/pages/store-locator"
                )
                page_url = page_url.replace("\\", "")
            else:
                locator_domain = "https://decathlon.lk/"
                page_url = "https://decathlon.lk/pages/store-locator"
            location_name = j.get("name")
            street_address = j.get("address") or ""
            street_address = street_address.replace("\\", "").replace("/", "")
            if street_address.endswith(","):
                street_address = street_address[:-1]
            if street_address.split(", ")[-1].count(" ") == 0:
                street_address = street_address.split(",")[0].strip()
            city = j.get("city")
            state = j.get("state")
            postal = j.get("postal")
            country = j.get("country")

            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("lng")
            store_number = j.get("id")

            _tmp = []
            source = j.get("schedule") or "<html></html>"
            tree = html.fromstring(source)
            hours = tree.xpath("//text()")
            for h in hours:
                h = (
                    h.replace("available from", "")
                    .replace(" |", ":")
                    .replace("\\r", "")
                    .strip()
                    .lower()
                )
                if (
                    not h
                    or "click" in h
                    or "open" in h
                    or "visit" in h
                    or "normal" in h
                ):
                    continue
                _tmp.append(h.strip())
                if "sunday" in h.lower():
                    break

            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country,
                store_number=store_number,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)

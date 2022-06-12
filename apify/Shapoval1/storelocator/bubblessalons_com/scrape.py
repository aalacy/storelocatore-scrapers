import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://locations.bubblessalons.com/"
    api_url = "https://locations.bubblessalons.com/search?q=washington+dc&r=100"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="location-list-resultContainer"]')
    for d in div:
        slug = "".join(d.xpath('.//a[@class="location-card-title-link"]/@href'))
        page_url = f"https://locations.bubblessalons.com/{slug}"
        location_name = "".join(d.xpath('.//span[@class="location-name-geo"]/text()'))
        street_address = (
            "".join(d.xpath('.//span[@class="c-address-street-1"]/text()'))
            + " "
            + "".join(d.xpath('.//span[@class="c-address-street-2"]/text()'))
        )
        street_address = street_address.strip()
        state = "".join(d.xpath('.//abbr[@class="c-address-state"]/text()'))
        postal = "".join(d.xpath('.//span[@class="c-address-postal-code"]/text()'))
        country_code = "US"
        city = "".join(d.xpath('.//span[@class="c-address-city"]/span[1]/text()'))
        phone = "".join(d.xpath('.//div[@itemprop="telephone"]/text()'))
        hours_js = "".join(
            d.xpath(
                './/div[@class="c-location-hours-details-wrapper js-location-hours"]/@data-days'
            )
        )
        h_js = json.loads(hours_js)
        hours_of_operation = "<MISSING>"
        tmp = []
        if h_js:
            for h in h_js:
                day = h.get("day")
                opens = str(h.get("intervals")[0].get("start"))
                closes = str(h.get("intervals")[0].get("end"))
                if len(str(opens)) == 4:
                    opens = opens[:2] + ":" + opens[2:]
                if len(str(opens)) == 3:
                    opens = opens[:1] + ":" + opens[1:]
                if len(str(closes)) == 4:
                    closes = closes[:2] + ":" + closes[2:]
                if len(str(closes)) == 3:
                    closes = closes[:1] + ":" + closes[1:]
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        latitude = "".join(
            tree.xpath(
                '//div[@id="schema-location"]//meta[@itemprop="latitude"]/@content'
            )
        )
        longitude = "".join(
            tree.xpath(
                '//div[@id="schema-location"]//meta[@itemprop="longitude"]/@content'
            )
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
            raw_address=f"{street_address} {city}, {state} {postal}",
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)

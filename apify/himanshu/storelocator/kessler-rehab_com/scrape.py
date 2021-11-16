import json
import re

from lxml import etree
from urllib.parse import urljoin

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.kessler-rehab.com//sxa/search/results/?s={75078478-6727-4E71-8FC2-BED8FAD1B00B}&itemid={AF08CF64-F629-40A6-81AA-0B56D5A0185A}&sig=locations-cards&o=Title%2CAscending&p=20&v=%7BDD817789-9335-4441-B604-DC2901221E22%7D"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    for poi in data["Results"]:
        poi_html = etree.HTML(poi["Html"])
        store_url = poi_html.xpath('//a[contains(text(), "View location")]/@href')[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath('//h3[@class="loc-result-card-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('//*[@class="loc-result-card-general"]//text()')
        street_address = raw_address[0].strip()
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            '//div[@class="loc-result-card-phone-container"]//a/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath("//@data-latlong")[0].split("|")
        latitude = geo[0]
        longitude = geo[1]
        hoo = poi_html.xpath(
            '//div[@class="mobile-container field-businesshours"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        sgw.write_row(
            SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)

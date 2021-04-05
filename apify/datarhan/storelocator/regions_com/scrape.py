import re
import json
from lxml import etree

from sgscrape.simple_utils import parallelize
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list
from sgrequests import SgRequests

SCRAPED_POI = []


def fetch_records_for(zipcode):
    with SgRequests() as session:
        start_url = "https://www.regions.com/Locator?regions-get-directions-starting-coords=&daddr=&autocompleteAddLat=&autocompleteAddLng=&r=&geoLocation={}&type=branch"
        response = session.get(start_url.format(zipcode))
        dom = etree.HTML(response.text)

        all_poi = dom.xpath('//script[contains(text(), "searchResults")]/text()')[0]
        all_poi = re.findall(
            "searchResults =(.+);", all_poi.replace("\r", "").replace("\n", "")
        )[0]
        all_poi = json.loads(all_poi.replace("/* forcing open state for all FCs*/", ""))
        all_urls = dom.xpath('//ol[@class="locator-results__list"]/li/a/@href')
        for poi in all_poi:
            if type(poi) == str:
                continue
            for url in all_urls:
                if poi["title"].replace(" ", "-").lower() in url.lower():
                    poi["store_url"] = url
                    break
            yield poi


def process_record(raw_results_from_one_zipcode):
    # parse, normalize, process raw results here
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    DOMAIN = "regions.com"

    all_poi = []
    for poi in raw_results_from_one_zipcode:
        if type(poi) == str:
            continue

        page_url = "<MISSING>"
        if not poi.get("store_url"):
            continue
        page_url = "https://www.regions.com" + poi["store_url"]
        location_name = poi["title"].replace("&#39;", "'")
        street_address = poi["address"].split("<br />")[0].replace("&#39;", "'")
        city = poi["address"].split("<br />")[-1].split(",")[0].replace("&#39;", "'")
        state = poi["address"].split("<br />")[-1].split(",")[-1].split()[0]
        zip_postal = poi["address"].split("<br />")[-1].split(",")[-1].split()[-1]
        country_code = "US"
        store_number = ""
        location_type = poi["type"]
        if "bank-branch" in page_url:
            location_type = "branch"
        latitude = poi["lat"]
        longitude = poi["lng"]

        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        phone = loc_dom.xpath('//a[@class="rds-link" and contains(@href, "tel")]/@href')
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Lobby Hours")]/following-sibling::ul[1]//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        check = "{} {}".format(location_name, street_address)
        if check not in SCRAPED_POI:
            SCRAPED_POI.append(check)

            all_poi.append(
                SgRecord(
                    locator_domain=DOMAIN,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )

    return all_poi


if __name__ == "__main__":
    with SgWriter() as writer:
        results = parallelize(
            search_space=static_zipcode_list(
                radius=30, country_code=SearchableCountries.USA
            ),
            fetch_results_for_rec=fetch_records_for,
            processing_function=process_record,
            max_threads=32,  # tweak to see what's fastest
        )
        for rec in results:
            writer.write_row(rec)

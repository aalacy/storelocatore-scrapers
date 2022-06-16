import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    domain = "kw.com"
    start_url = "https://api-endpoint.cons-prod-us-central1.kw.com/graphql"

    headers = {"x-shared-secret": "MjFydHQ0dndjM3ZAI0ZHQCQkI0BHIyM="}
    query = """{
        ListOfficeQuery {
            id
            name
            address
            subAddress
            phone
            fax
            lat
            lng
            url
            contacts {
            name
            email
            phone
            __typename
            }
            __typename
        }
        }
    """
    payload = {"operationName": None, "variables": {}, "query": query}
    response = session.post(start_url, headers=headers, json=payload)
    all_poi = response.json()
    all_poi = all_poi["data"]["ListOfficeQuery"]

    for poi in all_poi:
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        street_address = poi["address"]
        if poi["subAddress"]:
            street_address += " " + poi["subAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = ""
        state = ""
        zip_code = ""
        country_code = ""
        if store_url != "<MISSING>":
            loc_response = session.get(store_url)
            if loc_response.status_code == 200:
                loc_dom = etree.HTML(loc_response.text)
                data = loc_dom.xpath('//script[@id="__NEXT_DATA__"]/text()')
                if data:
                    data = json.loads(data[0])
                    if not data["props"]["pageProps"]["siteData"].get(
                        "marketCenterOptionsData"
                    ):
                        continue
                    if data["props"]["pageProps"]["siteData"][
                        "marketCenterOptionsData"
                    ]["data"]["SiteOptionsQuery"]:
                        poi_data = data["props"]["pageProps"]["siteData"][
                            "marketCenterOptionsData"
                        ]["data"]["SiteOptionsQuery"]["profile"]["profile"]["org_info"]
                        city = poi_data["org_address"]["city"]
                        state = poi_data["org_address"]["state"]
                        zip_code = poi_data["org_address"]["postal_code"]
                        country_code = poi_data["website_country"]
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = poi["__typename"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = ""

        item = SgRecord(
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

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()

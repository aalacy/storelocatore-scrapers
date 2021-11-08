import re
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "mynavyexchange.com"
    start_url = "https://www.mynavyexchange.com/storelocator/storeresults.jsp?searchMap=true&state={}"

    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    for state in states:
        response = session.get(start_url.format(state))
        all_locations = re.findall("storeid=(.+?)&", response.text)

        for store_number in all_locations:
            if not store_number.isdigit():
                continue
            store_url = "https://www.mynavyexchange.com/storelocator/storedetails.jsp?storeid={}&zipcode=&state={}&radius=&city=&country="
            store_url = store_url.format(store_number, state)
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            raw_address = loc_dom.xpath(
                '//h3[contains(text(), "ADDRESS")]/following-sibling::p[1]/text()'
            )
            raw_address = [
                " ".join([l.strip() for l in e.split()])
                for e in raw_address
                if e.strip()
            ][0].split(", ")
            location_name = loc_dom.xpath("//div/h2/text()")[0]
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            phone = loc_dom.xpath(
                '//dt[contains(text(), "Main:")]/following-sibling::dd/text()'
            )[0].strip()
            geo = re.findall(r"addMarker\((.+?)\);", loc_response.text)[0].split(", ")
            hoo = loc_dom.xpath(
                '//h4[contains(text(), " Regular:")]/following-sibling::div[1]//text()'
            )
            hoo = " ".join([e.strip() for e in hoo if e.strip()])

            item = SgRecord(
                locator_domain=domain,
                page_url=store_url,
                location_name=location_name,
                street_address=street_address,
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code=addr.country,
                store_number=store_number,
                phone=phone,
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=hoo,
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

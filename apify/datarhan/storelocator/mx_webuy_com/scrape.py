# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "mx.webuy.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    domains = [
        "mx.webuy.com",
        "es.webuy.com",
        "ic.webuy.com",
        "ie.webuy.com",
        "in.webuy.com",
        "nl.webuy.com",
        "pl.webuy.com",
        "pt.webuy.com",
        "au.webuy.com",
        "it.webuy.com",
    ]
    for d in domains:
        data = session.get(
            f"https://wss2.cex.{d.replace('.com', '')}.io/v3/stores", headers=hdr
        ).json()
        for poi in data["response"]["data"]["stores"]:
            store_number = poi["storeId"]
            page_url = f"https://{d}/site/storeDetail?branchId={store_number}"
            poi_data = session.get(
                f"https://wss2.cex.{d.replace('.com', '')}.io/v3/stores/{store_number}/detail"
            ).json()
            poi_data = poi_data["response"]["data"]["store"]
            street_address = poi_data["addressLine1"]
            if poi_data["addressLine2"]:
                street_address += " " + poi_data["addressLine2"]
            if street_address and street_address.endswith(","):
                street_address = street_address[:-1]
            hoo = []
            for day, opens in poi_data["timings"]["open"].items():
                hoo.append(f"{day}: {opens} - {poi_data['timings']['close'][day]}")
            hoo = " ".join(hoo)
            country_code = page_url.split("//")[1].split(".")[0]
            raw_address = (
                street_address + " " + poi_data["city"] + " " + poi["regionName"]
            )
            addr = parse_address_intl(raw_address)
            city = addr.city
            if city and "Loja" in city:
                city = ""
            if city and "Road" in city:
                city = ""

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["storeName"],
                street_address=street_address,
                city=city,
                state=addr.state,
                zip_postal=poi_data["postcode"],
                country_code=country_code,
                store_number=store_number,
                phone=poi["phoneNumber"],
                location_type="",
                latitude=poi["latitude"],
                longitude=poi["longitude"],
                hours_of_operation=hoo,
                raw_address=raw_address,
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

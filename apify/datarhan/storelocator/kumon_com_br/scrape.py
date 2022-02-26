# -*- coding: utf-8 -*-
# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()
    countries = {
        "AR": "https://www.kumon.com.ar/",
        "BR": "https://www.kumon.com.br/",
        "BO": "https://www.kumon.com.bo",
        "CL": "https://www.kumon.cl/",
        "CO": "https://www.kumon.com.co/",
        "PE": "https://www.kumon.com.pe/",
        "UY": "https://www.kumon.com.uy/",
    }

    for country, c_url in countries.items():
        start_url = (
            f"https://api.kumon.com.br/api/v1/stateWithCenters?=&country={country}"
        )
        domain = "kumon.com.br"
        hdr = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        data = session.get(start_url, headers=hdr).json()
        for state in data:
            url = f"https://api.kumon.com.br/api/v1/centers?neighborhood=&city=&state={state}&filterByLocation=true&Url=https://kumon.com.br/busca-de-unidades&country={country}"
            s_data = session.get(url).json()
            for poi in s_data["Centers"]:
                page_url = urljoin(c_url, poi["Url"])
                sun_hours = poi["Day1"] if poi["Day1"] else "closed"
                sunday = f"Sunday: {sun_hours}"
                monday = f'Monday: {poi["Day2"]}'
                tuesday = f'Tuesday: {poi["Day3"]}'
                wednesday = f'Wednesday: {poi["Day4"]}'
                thursday = f'Thursday: {poi["Day5"]}'
                friday = f'Friday: {poi["Day6"]}'
                saturday = f'Saturday: {poi["Day7"]}'
                hoo = f"{monday}, {tuesday}, {wednesday}, {thursday}, {friday}, {saturday}, {sunday}"

                item = SgRecord(
                    locator_domain=domain,
                    page_url=page_url,
                    location_name=poi["CenterName"],
                    street_address=poi["Address"],
                    city=poi["City"],
                    state=poi["State"],
                    zip_postal="",
                    country_code=poi["Country"],
                    store_number=poi["Id"],
                    phone=poi["Phone"],
                    location_type="",
                    latitude=poi["Latitud"],
                    longitude=poi["Longitud"],
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

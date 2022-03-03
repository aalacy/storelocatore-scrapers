# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal import sgpostal as parser
import lxml.html
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "dodge.cl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "dodge.cl",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "accept": "*/*",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "sec-ch-ua-platform": '"Windows"',
    "origin": "https://dodge.cl",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://dodge.cl/concesionarios",
    "accept-language": "en-US,en;q=0.9,ar;q=0.8",
}

data1 = {"rid": "", "localType": ""}

data2 = {"skid": ""}

cit_Data = {"com": ""}


def fetch_data():
    # Your scraper here
    search_url = "https://dodge.cl/concesionarios"
    with SgRequests() as session:
        search_res = session.get(search_url, headers=headers)

        search_sel = lxml.html.fromstring(search_res.text)
        regions = search_sel.xpath('//select[@class="form-control cboRegion"]/option')

        for region in regions[1:]:

            r_id = "".join(region.xpath("./@value"))
            stores = []
            if r_id == "13":
                region_url = "https://dodge.cl/Async/getDealersAndLocalsFromRegionWS"
                mdata = {"rid": "13", "localType": "ALL"}
                region_res = session.post(region_url, headers=headers, data=mdata)
                stores = json.loads(region_res.text)
            else:
                data1["rid"] = r_id  # update data1
                log.info(r_id)
                region_url = "https://dodge.cl/Async/getCommunesWithConces"
                region_res = session.post(region_url, headers=headers, data=data1)
                cities = json.loads(region_res.text)
                for cit in cities:
                    cit_Data["com"] = str(cit["id"])
                    cities_req = session.post(
                        "https://dodge.cl/Async/getLocalsInCom",
                        headers=headers,
                        data=cit_Data,
                    )
                    stores = json.loads(cities_req.text)

            for no, store in enumerate(stores, 1):

                sk_id = store["skId"]
                store_url = "https://dodge.cl/Async/getLocalInfoBySkId"
                data2["skid"] = sk_id

                store_res = session.post(store_url, headers=headers, data=data2)

                store_info = json.loads(store_res.text)
                if store_info.get("status"):
                    continue

                locator_domain = website

                location_name = store_info["nombre"]

                location_type = ""

                if store_info["tiene_ventas"] == "1":

                    raw_address = store_info["direccion"]

                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )

                    if street_address is not None:
                        street_address = street_address.replace("Ste", "Suite")
                    city = formatted_addr.city

                    state = formatted_addr.state
                    zip = formatted_addr.postcode

                    country_code = "CL"

                    phone = store_info.get("telefono_venta", "<MISSING>")
                    if phone:
                        phone = phone.split("/")[0].strip()

                    page_url = search_url

                    hour_list = []
                    try:
                        lunes_a_viernes = store_info["horario_semana"]
                        sabados = store_info["horario_sabados"]
                        domingos = store_info["horario_domingos"]

                        hour_list.append(f"Lunes a Viernes: {lunes_a_viernes}")
                        hour_list.append(f"Sábados: {sabados}")
                        hour_list.append(f"Domingos: {domingos}")
                    except:
                        pass

                    hours_of_operation = "; ".join(hour_list)

                    store_number = store_info["id_local_sk"]

                    latitude, longitude = (
                        store_info["latitud"],
                        store_info["longitud"],
                    )

                    yield SgRecord(
                        locator_domain=locator_domain,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

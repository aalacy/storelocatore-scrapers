# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import json
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

website = "pizzahutcr.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "authority": "pizzahutcr.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "cltlanguage": "ES",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "secauthcode": "dcdcce71ea1587010c27bbc5d5449a67ec7e1c4c08eeddffa9bf1a6657bd6738",
    "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryxML8AAN0Y2IPzKfi",
    "accept": "application/json, text/plain, */*",
    "cltdate": "2021-09-22 01:01:15",
    "sec-ch-ua-platform": '"Windows"',
    "cltip": "103.26.85.123",
    "origin": "https://pizzahutcr.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://pizzahutcr.com/external/",
    "accept-language": "en-US,en-GB;q=0.9,en;q=0.8",
}

data = {"Orden": "ubicacion_ocupado", "Activo": 1, "Estado": 1}


def fetch_data():
    # Your scraper here

    api_url = "https://pizzahutcr.com/internal/index.php/Api/index/Restaurantes/get"
    with SgRequests() as session:
        api_res = session.post(api_url, headers=headers, data=json.dumps(data))

        json_res = json.loads(api_res.text)

        store_list = json_res["data"]

        for store in store_list:

            page_url = "https://pizzahutcr.com/external/#!/allRestaurants"
            locator_domain = website
            location_name = store["Nombre_restaurante"].strip()
            if "Pizza Hut" not in location_name:
                continue
            street_address = store["Ubicacion_compania"]
            city = "<MISSING>"
            state = "<MISSING>"
            zip = "<MISSING>"

            country_code = "Costa Rica"
            phone = store["Telefono"]
            store_number = store["Id_restaurante"]

            location_type = "<MISSING>"

            hours = store["Horario"]
            hour_list = []
            for hour in hours:
                hour_list.append(
                    f"{hour['NombreDia']}: {hour['HorarioAperturaFormato']} - {hour['HorarioCerradoFormato']}"
                )

            hours_of_operation = "; ".join(hour_list)

            latitude, longitude = (
                store["Latitud"],
                store["Longitud"],
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

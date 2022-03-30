# -*- coding: utf-8 -*-

from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import os
import urllib
import zipfile
import time
import warnings
import pandas as pd
import ssl
import datetime
from tenacity import retry, stop_after_attempt
import tenacity


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


warnings.filterwarnings("ignore")
now = datetime.datetime.now()
current_time = now.strftime("%Y-%m-%d_%H%M%S")
logger = SgLogSetup().get_logger(logger_name="datahub_io__core__airport-codes")

headers_nomi = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "host": "nominatim.openstreetmap.org",
}


def download_and_get_dataframe(dir_name):
    url = f"https://datahub.io/core/airport-codes/r/{dir_name}.zip"

    extract_dir = f"./{dir_name}"
    if not os.path.exists(extract_dir):
        logger.info("Extract directory does not exist, creating it!")
        os.makedirs(extract_dir)
    logger.info(f"extract_dir: {extract_dir}")
    path_join = os.path.join(extract_dir, "data/airport-codes_csv.csv")
    if os.path.exists(path_join) is False:
        logger.info("Downloading and Extracting file")
        zip_path, _ = urllib.request.urlretrieve(url)
        logger.info(f"zip_path: {zip_path} | _ {_}")
        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(extract_dir)
        logger.info("Download Complete")
    else:
        logger.info("The file already downloaeded")
    df = pd.read_csv(path_join)
    return df


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(pagenum, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers_nomi)
        if response.status_code == 200:
            logger.info(f"<< {pagenum} | {response.status_code} OK!! >>")  # noqa
            return response
        raise Exception(f"<< Please Fix StoreUrlError {url} | {response.status_code}>>")


def fetch_data():
    dir_name = "airport-codes_zip"
    df_org = download_and_get_dataframe(dir_name)
    df = df_org.copy()

    # If iata_code is empty then remove those rows.
    # Number of iata_code having valid codes turned out to be 9149
    df_iata_notnull = df[(df["iata_code"].notnull())]

    # If iata_code contains dash, the remove those rows.
    df_filter_dash = df_iata_notnull[(df_iata_notnull["iata_code"].astype(str) != "-")]
    # iata_codes for some of the rows having zero, those should be removed.
    # We are only extracting the data for those airports are having iata_codes.
    df_filter_zero = df_filter_dash[(df_filter_dash["iata_code"].astype(str) != "0")]
    df_filter_zero = df_filter_zero.reset_index(drop=True)
    for idx, row in df_filter_zero.iterrows():
        DOMAIN = "datahub.io/core/airport-codes#data"
        page_url = "https://datahub.io/core/airport-codes#resource-airport-codes"
        location_name = ""
        default_location_name = row["name"]
        if default_location_name:
            location_name = default_location_name
        else:
            location_name = default_location_name
        coordinates = row["coordinates"]
        coord_lat = ""
        coord_lng = ""
        if coordinates:
            coord = coordinates.split(",")
            logger.info(coord)
            coord_lat = coord[1]
            coord_lng = coord[0]
        openstreetmap_url = "https://nominatim.openstreetmap.org"
        coord_lat = coord_lat.strip()
        coord_lng = coord_lng.strip()
        api_endpoint_url = f"{openstreetmap_url}/reverse?lat={coord_lat}&lon={coord_lng}&format=json&accept-language=en&addressdetails=1"
        r = get_response(idx, api_endpoint_url)
        rev_add_dict = r.json()
        time.sleep(1.5)
        raw_address = rev_add_dict["display_name"]
        logger.info(f"geo raw address: {raw_address}")
        lat = rev_add_dict["lat"]
        lng = rev_add_dict["lon"]

        street_address = ""
        if "road" in rev_add_dict["address"]:
            street_address = rev_add_dict["address"]["road"]

        city = ""
        municipality = row["municipality"]
        if "city" in rev_add_dict["address"]:
            city = rev_add_dict["address"]["city"]
        else:
            city = municipality

        state = ""
        if "state" in rev_add_dict["address"]:
            state = rev_add_dict["address"]["state"]

        cc = ""
        if "country_code" in rev_add_dict["address"]:
            cc = rev_add_dict["address"]["country_code"]
            cc = cc.upper()

        zip_postal = ""
        if "postcode" in rev_add_dict["address"]:
            zip_postal = rev_add_dict["address"]["postcode"]

        logger.info(
            f"[{idx}] => {street_address} | {city} | {state} | {zip_postal} | {cc}"
        )
        storeid = row["iata_code"]
        item = SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=cc,
            store_number=storeid,
            phone="",
            location_type=row["type"] or "",
            latitude=lat,
            longitude=lng,
            hours_of_operation="",
            raw_address=raw_address,
        )
        yield item


def scrape():
    logger.info(f"Started at {current_time}")  # noqa
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)
    logger.info(f"Finished at {current_time}")  # noqa


if __name__ == "__main__":
    scrape()
    logger.info("Finished")  # noqa

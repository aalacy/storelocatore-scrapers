from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("spencersonline")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.spencersonline.com/"
    base_url = "https://www.spencersonline.com/custserv/locate_store.cmd"
    with SgRequests() as session:
        res = session.post(base_url, headers=_headers).text
        total = int(res.split("allStores[")[-1].split("]")[0]) + 1
        logger.info(f"Total {total}")
        for i in range(1, total):
            logger.info(f"[{i}]")
            store_number = (
                res.split("store.STORE_NUMBER = '")[i]
                .split("store.ADDRESS_LINE_1")[0]
                .replace("';", "")
                .strip()
                .lstrip()
            )
            street_address = (
                res.split("store.ADDRESS_LINE_2 = '")[i]
                .split("store.CITY = '")[0]
                .replace("';", "")
                .replace("&#45;", "-")
                .strip()
            ) or "<MISSING>"
            if street_address == "X":
                continue
            latitude = (
                res.split("store.LATITUDE = '")[i]
                .split("store.LONGITUDE = '")[0]
                .replace("';", "")
                .strip()
            )
            longitude = (
                res.split("store.LONGITUDE = '")[i]
                .split("store.STORE_STATUS = '")[0]
                .replace("';", "")
                .strip()
            )
            zip_postal = (
                res.split("store.ZIP_CODE = '")[i]
                .split("store.PHONE = '")[0]
                .replace("';", "")
                .strip()
            )
            phone = (
                res.split("store.PHONE = '")[i]
                .split("store.LATITUDE = '")[0]
                .replace("';", "")
                .strip()
            )
            country_code = (
                res.split("store.COUNTRY_CODE ='")[i]
                .split("store.ZIP_CODE = '")[0]
                .replace("';", "")
                .strip()
            )
            state = (
                res.split("store.STATE ='")[i]
                .split("store.COUNTRY_CODE =")[0]
                .replace("';", "")
                .strip()
            )
            city = (
                res.split("store.CITY = '")[i]
                .split("store.STATE ='")[0]
                .replace("';", "")
                .strip()
            )
            location_name = (
                res.split("store.STORE_NAME = '")[i]
                .split("store.STORE_NUMBER = '")[0]
                .replace("';", "")
                .strip()
            )
            hours_of_operation = (
                res.split("store.STORE_STATUS = '")[i].split("';")[0].strip()
            )
            STORE_ID = (
                res.split("store.STORE_ID = '")[i]
                .split("store.STORE_NAME = '")[0]
                .replace("';", "")
                .strip()
            )
            page_url = (
                "https://www.spencersonline.com/store/"
                + str(location_name.strip().lstrip().replace(" ", "-"))
                + "/"
                + str(STORE_ID.strip().lstrip())
                + ".uts"
            )
            if "Coming Soon" in hours_of_operation:
                continue
            if hours_of_operation.find("Closed") != -1:
                hours_of_operation = "Closed"
            else:
                hours_of_operation = "<MISSING>"
            if latitude == "0" or longitude == "0":
                longitude = "<MISSING>"
                latitude = "<MISSING>"
            yield SgRecord(
                page_url=page_url,
                location_name=location_name,
                store_number=store_number,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                phone=phone,
                locator_domain=locator_domain,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

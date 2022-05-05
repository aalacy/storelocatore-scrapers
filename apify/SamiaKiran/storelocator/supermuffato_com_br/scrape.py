import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "supermuffato_com_br"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}

DOMAIN = "https://supermuffato.com.br/"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    if True:
        url = "https://institucional.supermuffato.com.br/webtools/services/api/NossasLojas.php"
        r = session.get(url, headers=headers)
        loclist = r.text.split("jsonLojas(")[1].split("}])")[0] + "}]"
        loclist = json.loads(loclist)
        for loc in loclist:
            location_name = strip_accents(loc["nmLoja"])
            log.info(location_name)
            loc_url = (
                "https://institucional.supermuffato.com.br/webtools/services/api/sm-rds-NossasLojas.php?action=getStore&callback=getStore&cdLoja="
                + loc["cdLoja"]
            )
            r = session.get(loc_url, headers=headers)
            temp = r.text.split("getStore(")[1].split("})")[0] + "}"
            temp = json.loads(temp)
            hours_of_operation = temp["14"].replace("|", "").split("\r\n")
            hours_of_operation = " ".join(hours_of_operation)
            if "Ou" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Ou")[0]
            phone = temp["8"]
            street_address = strip_accents(temp["nmLogradouro"])
            city = strip_accents(temp["txBairro"])
            try:
                state = strip_accents(temp["nmUf"])
            except:
                state = MISSING

            zip_postal = temp["nuCep"]
            try:
                coords = temp["urlMaps"].split("@")[1].split(",")
            except:
                coords = temp["urlMaps"].split("/")[-1].split(",")
            latitude = coords[0]
            longitude = coords[1]
            country_code = "BR"
            try:
                raw_address = strip_accents(
                    temp["1"]
                    + " "
                    + temp["2"].strip()
                    + " "
                    + temp["3"].strip()
                    + " "
                    + temp["4"].strip()
                    + " "
                    + temp["6"]
                    + " "
                    + temp["5"]
                    + " "
                    + temp["7"]
                )
            except:
                raw_address = strip_accents(
                    temp["1"]
                    + " "
                    + temp["2"].strip()
                    + " "
                    + temp["3"].strip()
                    + " "
                    + temp["4"].strip()
                    + " "
                    + temp["6"]
                    + " "
                    + temp["5"]
                )
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.supermuffato.com.br/lojas-fisicas/enderecos",
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


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

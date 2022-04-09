import json
import unicodedata
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "drogasil_com_br"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "site-bff-prod.drogasil.com.br",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.drogasil.com.br",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36",
}


DOMAIN = "https://drogasil.com.br/"
MISSING = SgRecord.MISSING

payload = json.dumps(
    {
        "operationName": "getStores",
        "variables": {
            "stores": "São Paulo",
            "regionName": "",
            "cityName": "",
            "neighborhood": "",
            "fullTime": "",
            "parking": "",
            "pharmacyPopular": "",
            "psychotropic": "",
            "itensPerPage": 5000,
            "activePage": 1,
        },
        "query": "query getStores($stores: String!, $regionName: String!, $cityName: String!, $neighborhood: String!, $fullTime: String!, $parking: String!, $pharmacyPopular: String!, $psychotropic: String!, $itensPerPage: Int!, $activePage: Int!) {\n  stores(\n    input: {searchText: {match: $stores}, regionName: {match: $regionName}, cityName: {match: $cityName}, neighborhood: {match: $neighborhood}, fullTime24h: {eq: $fullTime}, parking: {eq: $parking}, pharmacyPopular: {eq: $pharmacyPopular}, psychotropic: {eq: $psychotropic}, sort: {id: ASC}, pageSize: $itensPerPage, currentPage: $activePage}\n  ) {\n    page_info {\n      current_page\n      page_size\n      total_pages\n      total_count\n      __typename\n    }\n    items {\n      fantasyName\n      telephone\n      telephoneAreaCode\n      pharmacyPopular\n      psychotropic\n      parking\n      fullTime24h\n      address {\n        regionName\n        regionId\n        cityId\n        cityName\n        neighborhood\n        street\n        number\n        postcode\n        __typename\n      }\n      labelAttendance\n      __typename\n    }\n    filters {\n      regionName\n      cityName\n      neighborhood\n      pharmacyPopular\n      parking\n      fullTime24h\n      psychotropic\n      __typename\n    }\n    __typename\n  }\n}\n",
    }
)


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://site-bff-prod.drogasil.com.br/graphql"
        loclist = session.post(url, headers=headers, data=payload).json()["data"][
            "stores"
        ]["items"]
        for loc in loclist:
            location_name = strip_accents(loc["fantasyName"])
            store_number = MISSING
            phone = loc["telephone"]
            if "/" in phone:
                phone = phone.split("/")[0]
            phone = "(11) " + phone
            address = loc["address"]
            street_address = strip_accents(
                address["street"] + " " + address["number"].replace(",", ".")
            )
            log.info(street_address)
            city = strip_accents(address["cityName"])
            state = strip_accents(address["regionName"])
            zip_postal = address["postcode"]
            country_code = "BR"
            hours_of_operation = strip_accents(loc["labelAttendance"][0])
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.drogasil.com.br/nossas-lojas",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
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

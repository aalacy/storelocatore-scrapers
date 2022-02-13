from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Cookie": "ARRAffinity=e8b8d3148c29a06ebdae2d72da15134fada0945dbd963bce5c880255c35ebb72; ARRAffinitySameSite=e8b8d3148c29a06ebdae2d72da15134fada0945dbd963bce5c880255c35ebb72; .AspNetCore.Antiforgery.w5W7x28NAIs=CfDJ8Gh1N-Mm6ilPv9N490CiUlMvUsskJGqscbdbdcSPdnWvhFxKjiLC2iiiPc2L0Vh1k2S8fzsn7HbMN5zcHqRgjrC4RWlgKuQ6gU6YNxeTh3vycs3PouwYAf_fsyi6YDHNkdHo0JwBCuLK1LciveDm5-0; _ga=GA1.2.907074146.1609869384; _gid=GA1.2.609014934.1609869384; _gcl_au=1.1.356148459.1609869385; _fbp=fb.1.1609869385636.390311309; _gat=1",
    "RequestVerificationToken": "CfDJ8Gh1N-Mm6ilPv9N490CiUlPwipLb31Qgv4C5y2KuPzqnZpZX0V6dke465fek_7lXkDM4drwDGL1pQvvyR9gBLrfj0fUhnyrBDINgxzBB-LYvcvYUnnsNdqy401iKbXaJDOs5wPCKHWgs6smPLGeUXjY",
}

logger = SgLogSetup().get_logger("larosas_com")


def fetch_data():
    for pid in range(1, 150):
        logger.info(pid)
        url = "https://www.larosas.com/api/locations?handler=GetLocationsByStoreID"
        payload = {"id": pid, "pizzeriasOnly": "true"}
        r = session.post(url, headers=headers, data=payload)
        website = "larosas.com"
        typ = "<MISSING>"
        country = "US"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            if '"id":' in line:
                items = line.split('"id":')
                for item in items:
                    if "metaUrl" in item:
                        loc = item.split('"metaUrl":"')[1].split('"')[0]
                        store = item.split(",")[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        add = item.split('"streetAddress":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        lat = item.split('latitude":')[1].split(",")[0]
                        lng = item.split('longitude":')[1].split(",")[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        hours = item.split('"diningRoomHours":"')[1].split('"')[0]
                        hours = hours.replace("\\u003Cbr/\\u003E", "; ")
                        if hours == "":
                            hours = "<MISSING>"
                        hours = (
                            hours.replace("<br/>", "; ")
                            .replace("<br />", "; ")
                            .replace("<br>", "; ")
                        )
                        if "closed" not in name.lower():
                            yield SgRecord(
                                locator_domain=website,
                                page_url=loc,
                                location_name=name,
                                street_address=add,
                                city=city,
                                state=state,
                                zip_postal=zc,
                                country_code=country,
                                phone=phone,
                                location_type=typ,
                                store_number=store,
                                latitude=lat,
                                longitude=lng,
                                hours_of_operation=hours,
                            )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()

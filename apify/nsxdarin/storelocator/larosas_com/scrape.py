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
    "Cookie": "ARRAffinity=eeb07ed981018f5b52e2782779334447fffe71fbeeea9200f63be35f6a12f44a; ARRAffinitySameSite=eeb07ed981018f5b52e2782779334447fffe71fbeeea9200f63be35f6a12f44a; _gid=GA1.2.1309746962.1650226169; _gcl_au=1.1.1195149783.1650226169; ai_user=IbtUz|2022-04-17T20:09:29.200Z; _scid=63d870d2-fe27-402a-a144-eadd86fcb33f; _fbp=fb.1.1650226169697.449239281; _sctr=1|1650168000000; .AspNetCore.Antiforgery.w5W7x28NAIs=CfDJ8Cr3cY5hsCtFsO8Yv7yKxa1vyu9AYTG7VEiO36alCYbFxbkAsjSOYlPzUx8tzaA6XiQTYQLo9uH86iPpWIpyuPDxFx2GEzVZ67CyCAiVa2Uefq5-941m2z-gM_-cAL9GRK5kFAgvzWpzw_3j7w50Egc; _ga=GA1.1.1992558319.1650226169; _ga_XQLV2EFWD7=GS1.1.1650226169.1.1.1650226401.0; ai_session=1Ceh4|1650226170581|1650226507488.8",
    "RequestVerificationToken": "CfDJ8Cr3cY5hsCtFsO8Yv7yKxa3VeKcxluv-UDLzi1TfDiPby0QsTNkDfZwm974pjUeaJr90ufX_1Avo1GPSydUQw5qw_sq4o_keP74BbYluivW3a68Q6qXQwgP5FgaHUCEK0N_t-pOYqyEhveeU8m7hBls",
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

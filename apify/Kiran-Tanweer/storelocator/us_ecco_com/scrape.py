from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
import os


os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"

session = SgRequests()
website = "us_ecco_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "authority": "us.ecco.com",
    "method": "GET",
    "path": "/store-locator",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "__cfduid=dc8609779f425d4b6a5b722b414881ced1616285728; _gcl_au=1.1.1169164989.1616285731; _fbp=fb.1.1616285736624.1522925758; __cq_uuid=abyAXbXLHOSakqEdfKQLmLtks8; _gaexp=GAX1.2.5ubo4YhMSvmkB511OTImfQ.18774.0; _hjTLDTest=1; _hjid=7929f849-560f-44b5-b431-1ff9dfb1e3d5; cqcid=ab1RlULLFuyZkcPTpmZtQjDhES; cquid=||; dwpersonalization_7254072e2668c23dc3bf6cca213a6657=3018f310f8f2532a3cf7f2620320210328230000000; dwanonymous_7254072e2668c23dc3bf6cca213a6657=ab1RlULLFuyZkcPTpmZtQjDhES; __cq_dnt=0; dw_dnt=0; dw=1; dw_cookies_accepted=1; rmStore=amid:39558|dmid:7855|smid:7990c3eb-0fd1-486d-a04e-46b3e46dbfb7; _aeaid=33b93aa1-b332-448d-950c-392c442dbaf9; aeatstartmessage=true; _y2=1%3AeyJjIjp7IjE1NTIxMiI6MTQyMzAxODczLCIxNTU3MzQiOi0xNDczOTg0MDAwLCIxNTU5MTAiOi0xNDczOTg0MDAwfX0%3D%3ALTE0NzEzNjMxNjg%3D%3A99; stc113629=env:1617400784%7C20210503215944%7C20210402222944%7C1%7C1029797:20220402215944|uid:1616285736528.422307493.9166384.113629.444730999.9:20220402215944|srchist:1029797%3A1617400784%3A20210503215944:20220402215944|tsa:1617400784351.1906110256.0002856.34199548363158083:20210402222944; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; _ga_MJX5XBT1MQ=GS1.1.1617400783.4.0.1617401971.0; dwac_6c53ecadc6ec71a9636ab3a2d3=elLNftDcVORZTY303ChG8gsBBgzYr08Lbgc%3D|dw-only|||USD|false|US%2FEastern|true; sid=elLNftDcVORZTY303ChG8gsBBgzYr08Lbgc; dwsid=F6-tGne30Q0E8O0wZHZvN2b8Zmh_xMriM7rNye4bnS7ToMfOATR0f1Hgs2eP3Hk0xaKf0CDMB1GAL6ZfBovz3A==; _gid=GA1.2.1619389108.1618449844; _ga_3J4GNZ3HCG=GS1.1.1618449843.2.0.1618449843.0; _ga_S42WM01SGG=GS1.1.1618449843.5.0.1618449843.0; _ga=GA1.2.468868010.1616285733; stc115404=env:1618449844%7C20210516012404%7C20210415015404%7C1%7C1049721:20220415012404|uid:1616285863969.1663134451.372345.115404.307782940.7:20220415012404|srchist:1049721%3A1618449844%3A20210516012404:20220415012404|tsa:1618449844502.273821955.10759306.7219140410096259.:20210415015404; _uetsid=452212b09d8911ebb68bc16b902e746e; _uetvid=92a69ee089da11ebaf798d1318c74a83; _sp_ses.bc57=*; _hjIncludedInSessionSample=0; _hjAbsoluteSessionInProgress=0; _sp_id.bc57=04f52c4f9d5b7fb5.1616285862.2.1618450126.1616285908; _yi=1%3AeyJsaSI6eyJjIjowLCJjb2wiOjE2MTgyMjM1MzEsImNwZyI6MTU1MjEyLCJjcGkiOjUwMTY0OTI5NDYyLCJzYyI6MSwidHMiOjE2MTYyODU4NzMzNTF9LCJzZSI6eyJjIjoyLCJlYyI6MTEsImxhIjoxNjE4NDUwMTI3ODIyLCJwIjoxLCJzYyI6MjczfSwidSI6eyJpZCI6IjM2MTU4NTgwLWZjOGItNDIwMC05YzBmLTgxYWFkOWI1N2E0MSIsImZsIjoiMCJ9fQ%3D%3D%3ALTE5NjU3ODQwMA%3D%3D%3A99",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like GeneratorExitcko) Chrome/89.0.4389.114 Safari/537.36",
}


DOMAIN = "https://us.ecco.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        dedup = []
        url = "https://us.ecco.com/store-locator"
        stores_req = session.get(url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        scripts = soup.findAll("script")[19]
        scripts = str(scripts)
        locations = scripts.split('},{"storeID"')
        for loc in locations:
            loc = loc + "}"
            store = loc.split('"isECCOStore":')[1].split("}")[0]
            if store == "true":
                storeid = loc.split('","name"')[0]
                storeid = storeid.lstrip(':"').strip()
                title = loc.split('"name":"')[1].split('","')[0].strip()
                street = loc.split('"address1":"')[1].split('","')[0].strip()
                address = loc.split('"address":"')[1].split('","')[0].strip()
                pcode = address.split(",")[-1].strip()
                city = loc.split('"city":"')[1].split('","')[0].strip()
                state = loc.split('"stateCode":"')[1].split('","')[0].strip()
                country = loc.split('"countryCode":"')[1].split('","')[0].strip()
                phone = loc.split('"phone":"')[1].split('","')[0].strip()
                phone = phone.lstrip("+")
                if phone == "":
                    phone = "<MISSING>"
                lat = loc.split('"latitude":')[1].split(',"')[0]
                lng = loc.split('"longitude":')[1].split(',"')[0]
                if lat == "null":
                    lat = "<MISSING>"
                if lng == "null":
                    lng = "<MISSING>"
                hours = loc.split('"storeHours":')[1].split('],"')[0]
                hours = hours.split("},{")
                hoo = ""
                for hr in hours:
                    day = hr.split('"label":"')[1].split('","')[0]
                    hour = hr.split('"data":"')[1].split('"')[0]
                    h1 = day + " " + hour
                    hoo = h1 + " " + hoo
                street = street.strip()

                data_dedup = street + "-" + city + "-" + state + "-" + pcode
                if data_dedup not in dedup:
                    dedup.append(data_dedup)
                    if street != "4000 ARROWHEAD BLVD STE 874":
                        yield SgRecord(
                            locator_domain=DOMAIN,
                            page_url=url,
                            location_name=title,
                            street_address=street,
                            city=city,
                            state=state,
                            zip_postal=pcode,
                            country_code=country,
                            store_number=storeid,
                            phone=phone,
                            location_type="ECCO Store",
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hoo.strip(),
                        )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()

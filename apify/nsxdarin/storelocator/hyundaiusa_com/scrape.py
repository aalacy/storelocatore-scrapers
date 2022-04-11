import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=45,
)

logger = SgLogSetup().get_logger("hyundaiusa_com")

session = SgRequests()
headers = {
    "authority": "www.hyundaiusa.com",
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.hyundaiusa.com/us/en/dealer-locator",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "check=true; AMCVS_3C3BCE0154FA24300A4C98A1%40AdobeOrg=1; mboxEdgeCluster=34; s_ecid=MCMID%7C38173915453045790993218699860712968241; AMCV_3C3BCE0154FA24300A4C98A1%40AdobeOrg=1585540135%7CMCMID%7C38173915453045790993218699860712968241%7CMCAAMLH-1632329806%7C9%7CMCAAMB-1632329806%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1631732208s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; _gcl_au=1.1.1301855102.1631725015; AMCVS_C3BCE0154FA24300A4C98A1%40AdobeOrg=1; _ga=GA1.2.390822095.1631725025; _gid=GA1.2.1819423899.1631725025; s_cc=true; LPVID=Q4MzU2MmI5M2NiOWU2Y2E3; LPSID-41916303=atCq3AkuQom1HMSln9GjdA; _fbp=fb.1.1631725039793.1436195651; _scid=c650e539-7734-4fe5-be99-98decd483e34; _hjid=73d77c0a-b0a2-49f8-b724-f27553b8f0e8; _hjFirstSeen=1; _hjIncludedInSessionSample=0; _hjAbsoluteSessionInProgress=0; _pin_unauth=dWlkPU9Ua3hZamt6WTJVdFlUYzJNUzAwTm1VM0xUZzBObUV0TUdNNE5tSXhOVFUxWldZeA; _sctr=1|1631642400000; ipe_s=e4b81652-6ea2-1040-38fa-6b0504332ad1; IPE_LandingTime=1631725060568; ipe.322.pageViewedDay=258; s_sq=%5B%5BB%5D%5D; AMCV_C3BCE0154FA24300A4C98A1%40AdobeOrg=1585540135%7CMCMID%7C38173915453045790993218699860712968241%7CMCIDTS%7C18886%7CMCAID%7CNONE%7CMCOPTOUT-1631732351s%7CNONE%7CvVersion%7C4.4.0; s_ppn=find%20a%20dealer; _uetsid=febca940164511ecabbf931e7e1a4e31; _uetvid=febcdd50164511ecbb4f0b2d2f23b74d; s_ppvl=find%2520a%2520dealer%2C44%2C44%2C917%2C1920%2C917%2C1920%2C1080%2C1%2CP; ipe.322.pageViewedCount=2; _aeaid=f2b9ac37-35ae-4e4d-9a87-3a5cc2a6c70d; aeatstartmessage=true; re-evaluation=true; ipe_322_fov=%7B%22numberOfVisits%22%3A1%2C%22sessionId%22%3A%22e4b81652-6ea2-1040-38fa-6b0504332ad1%22%2C%22expiry%22%3A%222021-10-15T16%3A57%3A40.577Z%22%2C%22lastVisit%22%3A%222021-09-15T17%3A01%3A10.651Z%22%7D; s_ppv=find%2520a%2520dealer%2C44%2C44%2C917%2C1920%2C427%2C1920%2C1080%2C1%2CP; utag_main=v_id:017bea63d9ac00122f7a546323b703068002006000bd0$_sn:1$_se:7$_ss:0$_st:1631727138658$ses_id:1631725017517%3Bexp-session$_pn:3%3Bexp-session$vapi_domain:hyundaiusa.com; _gat_UA-170970756-1=1; _gat_UA-171252554-1=1; mbox=session#16b5c03687234a789f53ba31432ca350#1631726865|PC#16b5c03687234a789f53ba31432ca350.34_0#1694970140; __atuvc=3%7C37; __atuvs=614225cca3eae8ba002",
}


def fetch_data():
    for code in search:
        logger.info(code)
        url = (
            "https://www.hyundaiusa.com/var/hyundai/services/dealer/dealersByZip.json?brand=hyundai&model=all&lang=en_US&zip="
            + code
            + "&maxdealers=45"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '{"cobaltDealerURL":"' in line:
                items = line.split('{"cobaltDealerURL":"')
                for item in items:
                    if '"redCapUrl":' in item:
                        website = "hyundaiusa.com"
                        typ = "<MISSING>"
                        try:
                            loc = item.split('"')[0]
                        except:
                            loc = "<MISSING>"
                        store = item.split('"dealerCd":"')[1].split('"')[0]
                        name = item.split('"dealerNm":"')[1].split('"')[0]
                        logger.info(name)
                        add = (
                            item.split('"address1":"')[1].split('"')[0]
                            + " "
                            + item.split('"address2":"')[1].split('"')[0]
                        )
                        add = add.strip()
                        country = "US"
                        city = item.split('"city":"')[1].split('"')[0]
                        zc = item.split(',"zipCd":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phone":"')[1].split('"')[0]
                        except:
                            phone = "<MISSING>"
                        try:
                            lat = item.split('"latitude":')[1].split("e")[0]
                            lng = item.split('"longitude":')[1].split("e")[0]
                            lat = float(lat) * 100
                            lng = float(lng) * 100
                            if lat >= 100:
                                lat = float(lat) / 10
                            if lng >= -50:
                                lng = float(lng) * 10
                            if lng <= -181:
                                lng = float(lng) / 10
                            lat = str(lat)
                            lng = str(lng)
                        except:
                            lat = "<MISSING>"
                            lng = "<MISSING>"
                        hour_list = json.loads(
                            item.split('"operations":')[1].split(',"vendorName"')[0]
                        )
                        hours = ""
                        for hour in hour_list:
                            hours = hours + " " + hour["day"] + " " + hour["hour"]
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
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()

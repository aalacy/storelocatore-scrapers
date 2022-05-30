from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from bs4 import BeautifulSoup as bs
import dirtyjson as json
from sglogging import SgLogSetup
import re
import time
from tenacity import retry, stop_after_attempt
import tenacity

logger = SgLogSetup().get_logger("carrefour")

_headers = {
    "authority": "www.carrefour.fr",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "service-worker-navigation-preload": "true",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://www.carrefour.fr/magasin",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "visid_incap_441619=5PdAmdLOSh2hanY8ltlP96zSsmEAAAAAQUIPAAAAAACmTMFUfuHNa+LrRUuRc08Y; visid_incap_1722501=wbplZ0omQWezPuRsfq/fRJTTsmEAAAAAQUIPAAAAAACfLWPkcHV0WnGfYwWvrQg4; FRONTONE_USER=1641701528; FRONTONE_SESSION_ID=569882306be10a47f47566d7569970648b80dd42; tc_cj_v2_cmp=; tc_cj_v2_med=; tc_ab=1; visid_incap_2237321=A3la7wi8Th+O79qS1FlUrKLTsmEAAAAAQUIPAAAAAACnBI9VRdsraAtdPJ6jcRbD; OptanonAlertBoxClosed=2021-12-10T04:12:28.368Z; OneTrustGroupsConsent=%2CC0048%2CC0001%2C; incap_ses_1122_441619=n/TILdFtyGRueJ+oeyWSD9JrvGEAAAAA9GL5hKLNURgnRzZ4SdB1mg==; nlbi_441619=UxW0XtWV4QF+L0kQpEl6HgAAAAApDitQGRZTYwlTKvJHC1Pe; incap_ses_993_441619=spDGUzaDcDS3pys6xNjHDexrvGEAAAAA1g1sirxGBCps0+E1mUNKzw==; FRONTONE_SESSID=8hun0d4bm1h7lrcpvad9bgsvlj; tc_cj_v2=%5Ecl_%5Dny%5B%5D%5D_mmZZZZZZKPMSQMRMOLQMOZZZ%5D; eupubconsent-v2=CPQ_ERtPQ_ERtAcABBENB6CgAAAAAAAAAChQAAAAAAAA.YAAAAAAAAAAA; aaaaaaaaa944fac35b02f4d9a99619247b88ad463_cs_nt=; incap_ses_988_441619=u8uRBVRfNDCou/arTxW2DWtyvGEAAAAACLGSooBCHg4h8d6vl17RgA==; pageCounterCrfOne=2; incap_ses_8221_441619=AuINblKje2UOV25TPtwWcodyvGEAAAAAzcIZCIr/xLPPX8dj0NldTQ==; QueueITAccepted-SDFrts345E-V3_prodevent=EventId%3Dprodevent%26QueueId%3D3d30969e-54ab-4a96-acd1-1e40846a54bc%26RedirectType%3Dsafetynet%26IssueTime%3D1639740041%26Hash%3D5e29c8ea8779958e5ad3ccd9658ac7a8f6b42df8f1e6fc1a1314da4366f92865; OptanonConsent=isIABGlobal=false&datestamp=Fri+Dec+17+2021+17%3A20%3A44+GMT%2B0600+(Bangladesh+Standard+Time)&version=6.12.0&hosts=&consentId=8a4a4724-87fc-4095-9492-56286f495020&interactionCount=1&landingPath=NotLandingPage&groups=C0048%3A1%2CC0001%3A1%2CC0040%3A0%2CC0032%3A0%2CC0025%3A0%2CC0020%3A0%2CC0037%3A0%2CC0039%3A0%2CC0036%3A0%2CC0041%3A0%2CC0042%3A0%2CC0044%3A0%2CC0043%3A0%2CC0045%3A0%2CC0046%3A0%2CC0049%3A0%2CC0050%3A0%2CC0047%3A0%2CC0023%3A0%2CC0056%3A0%2CC0065%3A0%2CC0137%3A0%2CC0038%3A0%2CC0082%3A0%2CC0021%3A0%2CC0004%3A0%2CC0022%3A0%2CC0054%3A0%2CC0146%3A0%2CC0052%3A0%2CC0035%3A0%2CC0034%3A0%2CC0063%3A0%2CC0157%3A0%2CC0051%3A0%2CC0136%3A0%2CC0135%3A0%2CC0007%3A0%2CSTACK1%3A0%2CSTACK42%3A0&geolocation=US%3BMN&AwaitingReconsent=false; datadome=.8dk7DZSAwLns2U3XpbHqEge4t9kc.YdB63opTPZWlPS2mdJIU9DBCjOc-GC_Ibg6WqF.Zj8W-iNxZB1xj_kTj6AF~8CcmswENuK3T99c0v057DdiLvn0oCLDy5B-~ak; datadome=.BaZb_6H_nMX9O.D3LV1ma.goksdsoh~WFWrOX9caczMn.V9Ay06O219FV9kA~QIR3lMSEZUYwJNBFjXwKiGRAT0NNt2Kvl-.jD1rPB.0zrlF.oHq5DqfVIEV6fk9bMN; incap_ses_1460_441619=0bHIcGXbKVxH1XW0X/ZCFP1yvGEAAAAAmIUDCDfHRlIkMd9E5EBb2A==",
}

locator_domain = "https://www.carrefour.fr"
base_url = "https://www.carrefour.fr/magasin/"


@retry(stop=stop_after_attempt(8), wait=tenacity.wait_fixed(8))
def get_response(url):
    logger.info("Retrying with Tenacity")
    with SgRequests(proxy_country="us") as http:
        try:
            response = http.get(url, headers=_headers)
            logger.info(f"{url} >> STATUS: {response.status_code}")

            if response.status_code == 200:
                logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
                return response
        except Exception as e:
            logger.info(f"Not loading page: {response.status_code} : {e}")
            pass


def fetch_data():
    with SgRequests(retries_with_fresh_proxy_ip=7) as session:
        regions = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "li.store-locator-footer-list__item a"
        )
        for region in regions:
            url = locator_domain + region["href"]
            locations = json.loads(
                session.get(url, headers=_headers)
                .text.split(":context-stores=")[1]
                .split(":context-filters")[0]
                .replace("&quot;", '"')
                .strip()[1:-1]
            )
            for _ in locations:
                addr = _["address"]
                street_address = addr["address1"]
                if addr["address2"]:
                    street_address += " " + addr["address2"]
                hours = []
                page_url = locator_domain + _["storePageUrl"]
                try:
                    for day, hh in (
                        _.get("openingWeekPattern", {}).get("timeRanges", {}).items()
                    ):
                        start = hh["begTime"]["date"].split()[-1].split(".")[0]
                        end = hh["endTime"]["date"].split()[-1].split(".")[0]
                        hours.append(f"{day}: {start} - {end}")
                except Exception as e:
                    logger.info(f" HOO Error: {e}")
                    pass

                phone = ""
                location_name = _["name"].replace("&#039;", "'")
                if page_url != base_url:
                    logger.info(page_url)
                    res = session.get(page_url, headers=_headers)
                    logger.info(f"2nd level: {res.status_code}")
                    time.sleep(1)
                    if res.status_code == 404:
                        continue
                    if res.status_code == 200:
                        sp1 = bs(res.text, "lxml")
                        location_name = sp1.select_one(
                            "h1.store-page__banner__heading"
                        ).text.strip()
                        location_type = json.loads(
                            sp1.find(
                                "script", string=re.compile(r"tc_vars = Object.assign")
                            )
                            .string.split("tc_vars = Object.assign(tc_vars,")[1]
                            .strip()[:-2]
                        )["store_format"]
                        if sp1.select_one("div.store-meta--telephone a"):
                            phone = sp1.select_one(
                                "div.store-meta--telephone a"
                            ).text.strip()
                        hours = []
                        for hh in sp1.select(
                            "div.store-hours div.store-meta__opening-range"
                        ):
                            day = hh.select_one("div.store-meta__label").text.strip()
                            times = ", ".join(
                                hh.select_one("div.store-meta__time").stripped_strings
                            )
                            hours.append(f"{day}: {times}")
                    else:
                        res = get_response(page_url)
                        if res:
                            sp1 = bs(res.text, "lxml")
                            location_name = sp1.select_one(
                                "h1.store-page__banner__heading"
                            ).text.strip()
                            location_type = json.loads(
                                sp1.find(
                                    "script",
                                    string=re.compile(r"tc_vars = Object.assign"),
                                )
                                .string.split("tc_vars = Object.assign(tc_vars,")[1]
                                .strip()[:-2]
                            )["store_format"]
                            if sp1.select_one("div.store-meta--telephone a"):
                                phone = sp1.select_one(
                                    "div.store-meta--telephone a"
                                ).text.strip()
                            hours = []
                            for hh in sp1.select(
                                "div.store-hours div.store-meta__opening-range"
                            ):
                                day = hh.select_one(
                                    "div.store-meta__label"
                                ).text.strip()
                                times = ", ".join(
                                    hh.select_one(
                                        "div.store-meta__time"
                                    ).stripped_strings
                                )
                                hours.append(f"{day}: {times}")

                yield SgRecord(
                    page_url=page_url,
                    store_number=_["id"],
                    location_name=location_name,
                    street_address=street_address.replace("&#039;", "'"),
                    city=addr["city"].replace("&#039;", "'"),
                    state=addr["region"],
                    zip_postal=addr["postalCode"],
                    latitude=addr["geoCoordinates"]["latitude"],
                    longitude=addr["geoCoordinates"]["longitude"],
                    country_code="FR",
                    phone=phone,
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

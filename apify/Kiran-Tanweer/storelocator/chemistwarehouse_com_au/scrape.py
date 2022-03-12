from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup

session = SgRequests()
website = "chemistwarehouse_com_au"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "X-Requested-With": "XMLHttpRequest",
    "Connection": "keep-alive",
    "Referer": "https://www.chemistwarehouse.com.au/aboutus/store-locator",
    "Cookie": "__cf_bm=StVSvKrR_o2PrQ5PAVMAqF.yH6MbYBU.hNcFX30K6Ks-1644758022-0-Ae3OevPwvCEpw0g0S2vY9E1YMW8oGt2ppHIHcAISew7qG5ZvTcopVaCgPaeuqCEEkdc+B/7eC4qNh4ZzE7Itgkp9cM1ceJMHbQj+EOhj2kB190bawEpPL132dn5WSDH0SxqGTikTc8fpjqfhJTnY3LwCsJaInOg0K4iUlYirJay9; __cflb=02DiuDfFR9ebh77hQy3o3iRnxnF3ZbZdhZMfYd3DTRS5z; optimizelyEndUserId=oeu1644758020623r0.3445548448271267; BVImplmain_site=13773; ASP.NET_SessionId=1vyohz31tj0fh01ybxk4vuft; sift=uid=&sid=1vyohz31tj0fh01ybxk4vuft&ipad=2400:adc1:482:2500:fc9a:e556:bdab:2b1d; CacheUpdater=%5B%7B%22numItemsInCart%22%3A0%2C%22totalAmountInCart%22%3A%22%240.00%22%2C%22boolShowYellowBox%22%3A%22False%22%2C%22needMoreAmountForFreeShipping%22%3A%22%240.00%22%2C%22boolLoggedIn%22%3A%22False%22%2C%22userFName%22%3A%22%22%2C%22country%22%3A284%2C%22shippingfee%22%3A%22%240.00%22%7D%5D; BVBRANDID=9a4d25e0-07f5-46a2-b2cc-9655d5a73551; BVBRANDSID=6f6710f7-1389-494e-82db-3099ebbb3ee3; country_code=PK; country_code=PK; region_code=SD; pcf=true; _gcl_au=1.1.1036938234.1644758025; gtm.custom.bot.flag=human; _ga_LL1Y7PBG36=GS1.1.1644758025.1.1.1644758046.0; _ga=GA1.3.1317764767.1644758025; rmStore=dmid:9399; xyz_cr_536_et_100==NaN&cr=536&wegc=&et=100&ap=; stc117346=tsa:1644758025777.1215059663.34729.7734965266987871.20:20220213134407|env:1%7C20220316131345%7C20220213134407%7C2%7C1068405:20230213131407|uid:1644758025776.1425899283.1459591.117346.1128167865:20230213131407|srchist:1068405%3A1%3A20220316131345:20230213131407; _cls_v=cdeb4055-3c62-4990-b0f2-f7953951db6d; _cls_s=78441cbe-5521-43b8-86ea-900d3826d7d4:0; meiro_user_id_js=0566bc89-24be-443b-900a-75bb15f7ccd7; _pin_unauth=dWlkPVl6Z3dOR1U1T1RrdFpXWmpZaTAwT0RjMExXSTJPVGt0TkdJNE56aGhOalJoWW1ReQ; emailsignupbox=1; _gid=GA1.3.2024648261.1644758028; _fbp=fb.2.1644758029274.767459544; __qca=P0-12113558-1644758030758; outbrain_cid_fetch=true; __gads=ID=ee2f9177ddc27ba3-22f20a98e0cf003a:T=1644758031:S=ALNI_MaHVA79z4xDtiWC5v_gSC4vnH4w5A; cto_bundle=wMIlUF9zZUdVOFN5Z0ZuQnBOZ1JFQmJTREZ4UTdGWTFBODJTcW90UnIlMkJmRHlmTGQlMkZDc3VFTExvcmFnckZmRjg0RyUyQkFwJTJCYlRIcGlib09PMkJjQXBaNVdNd3VTakE4bVdVQ3ZScUlzUkQ5Y0olMkY4WVg1S2wxU2NpSVg0WUpKWklqb1dZWFJpdWVFT1N1S2tuSkpiJTJCd0gyUiUyQmN4dyUzRCUzRA; _uetsid=c6311c708cce11ecb8c3a13d10699d74; _uetvid=c63146808cce11ec86523ff2ca0d9b6c; __cf_bm=AP.AU1NtduD3LDw5RireX2JM7x_m7q8USbEPEX71JcM-1644759493-0-Ad5Bwc3cdIB+JfltD/gf+re3Rcizz/dTV1yFh7H+J4tt3kc+Nm5zMsMCIC06w+saE2L0GHDIeHkscRbNujx6azM=",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}
DOMAIN = "https://chemistwarehouse.com.au/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.chemistwarehouse.com.au/ams/webparts/Google_Map_SL_files/storelocator_data.ashx?searchedPoint=(-35.1423355,%20149.0353134)"
        stores_req = session.get(search_url, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        markers = soup.findAll("marker")
        for store in markers:
            title = store["storename"]
            storeid = store["id"]
            lat = store["lat"]
            lng = store["lng"]
            hours = (
                "Mon "
                + store["storemon"]
                + " tues "
                + store["storetue"]
                + " wed "
                + store["storewed"]
                + " thurs "
                + store["storethu"]
                + " fri "
                + store["storefri"]
                + " sat "
                + store["storesat"]
                + " Sun "
                + store["storesun"]
            )
            street = store["storeaddress"]
            phone = store["storephone"]
            pcode = store["storepostcode"]
            state = store["storestate"]
            city = store["storesuburb"]
            hours = hours.strip()

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="AU",
                store_number=storeid,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
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

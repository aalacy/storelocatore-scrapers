from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


def fetch_data():
    base_url = "https://www.screwfix.com/"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cookie": "JSESSIONID=vH3-MNO6uamFPOgCUHNBd2lLWm4Aj5r5FDJCTnSc9FzADBus9N0M!-639553274; BIGipServersfx.com_HTTPS_Pool=!WMFmpd4F10iTNKjJ7bks1SOITn8qcS+sMTOif4HYB6ECNdz026yXsT37hj79n2hcuLT499u11dRl; rxVisitor=1610582384050Q6LU5N4IQR2LLCFLCSFK3E9NMN8AR79D; notice_behavior=expressed,eu; localtesting_cookie=undefined; dtCookie==3=srv=1=sn=71AF00ADC812CD40DE3D07909DBE9800=perc=100000=ol=0=mul=1=app:c4f0aebc3d79082a=1; notice_preferences=4:; notice_gdpr_prefs=0,1,2,3,4:; TAconsentID=74bd69dd-57f2-4031-83b7-61e0b4096b3f; cmapi_gtm_bl=; cmapi_cookie_privacy=permit 1,2,3,4,5; _gdprCookie=AcceptAll; _ga=GA1.2.502071418.1610582407; _gid=GA1.2.1392670159.1610582407; _mibhv=anon-1610582408983-8322565947_4997; _gcl_au=1.1.1650900528.1610582410; dtSa=-; _gat_tealium_0=1; utag_main=v_id:0176fe30ea250019e725e5eca79103073001906b00bd0$_sn:1$_ss:0$_st:1610584305883$ses_id:1610582387238%3Bexp-session$_pn:4%3Bexp-session$dc_visit:1$dc_event:4%3Bexp-session$dc_region:us-east-1%3Bexp-session; _uetsid=76982a8055fb11ebaca673dce6b50c70; _uetvid=769836c055fb11eb8f4b6fe275117221; _br_uid_2=uid%3D3245210081443%3Av%3D13.0%3Ats%3D1610582392135%3Ahc%3D4; rxvt=1610584308577|1610582384052; dtPC=1$182505733_635h-vMTWILDPUGAKAMWOAMBUPERHSRREUUPSJ-0e5; dtLatC=1",
        "referer": "https://www.screwfix.com/jsp/tradeCounter/tradeCounterPage.jsp",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }
    with SgRequests() as session:
        r = session.get(
            "https://www.screwfix.com/jsp/tradeCounter/tradeCounterAllStoresPage.jsp",
            headers=headers,
        )
        soup = bs(r.text, "lxml")
        detail_links = soup.select("ul.store-name li a")
        for detail_link in detail_links:
            page_url = base_url + detail_link["href"]
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "cookie": "BIGipServersfx.com_HTTPS_Pool=!WMFmpd4F10iTNKjJ7bks1SOITn8qcS+sMTOif4HYB6ECNdz026yXsT37hj79n2hcuLT499u11dRl; rxVisitor=1610582384050Q6LU5N4IQR2LLCFLCSFK3E9NMN8AR79D; notice_behavior=expressed,eu; localtesting_cookie=undefined; dtCookie==3=srv=1=sn=71AF00ADC812CD40DE3D07909DBE9800=perc=100000=ol=0=mul=1=app:c4f0aebc3d79082a=1; notice_preferences=4:; notice_gdpr_prefs=0,1,2,3,4:; TAconsentID=74bd69dd-57f2-4031-83b7-61e0b4096b3f; cmapi_gtm_bl=; cmapi_cookie_privacy=permit 1,2,3,4,5; _gdprCookie=AcceptAll; _ga=GA1.2.502071418.1610582407; _gid=GA1.2.1392670159.1610582407; _mibhv=anon-1610582408983-8322565947_4997; _gcl_au=1.1.1650900528.1610582410; JSESSIONID=tYz_524EDVk2J4A5W3FL5lUG2-guY-tk0JNQZGxGT9QdMjLMO_tj!-973958274; utag_main=v_id:0176fe30ea250019e725e5eca79103073001906b00bd0$_sn:2$_ss:1$_st:1610612931572$dc_visit:2$ses_id:1610611131572%3Bexp-session$_pn:1%3Bexp-session$dc_event:1%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session; _br_uid_2=uid%3D3245210081443%3Av%3D13.0%3Ats%3D1610582392135%3Ahc%3D8; _uetsid=76982a8055fb11ebaca673dce6b50c70; _uetvid=769836c055fb11eb8f4b6fe275117221; _gat_tealium_0=1; rxvt=1610612959281|1610611126719; dtPC=1$211126712_232h-vPDRMMPRFRRPHBHPFAROCCWARJEGCGKFU-0e10; dtLatC=295; dtSa=true%7CC%7C-1%7CIrlam%7C-%7C1610611168221%7C211126712_232%7Chttps%3A%2F%2Fwww.screwfix.com%2Fjsp%2FtradeCounter%2FtradeCounterAllStoresPage.jsp%7CScrewfix%20Stores%20%5Ep%20Screwfix%20Website%7C1610611160547%7C%7C",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            }
            soup1 = bs(session.get(page_url, headers=headers).text, "lxml")
            addr = parse_address_intl(soup1.select_one("address").text.strip())
            location_name = soup1.select_one("span.tcName").string
            hours = [
                _.text.strip() for _ in soup1.select("li.sl__store.sl__store dl dd")
            ]
            country_code = soup1.select_one("input#defaultCountryCode")["value"]
            store_number = soup1.select_one("input#storeId")["value"]
            latitude = soup1.select_one("input#lat")["value"]
            longitude = soup1.select_one("input#lng")["value"]

            yield SgRecord(
                page_url=page_url,
                store_number=store_number,
                location_name=location_name,
                street_address=addr.street_address_1,
                city=addr.city,
                state=addr.state,
                latitude=latitude,
                longitude=longitude,
                zip_postal=addr.postcode,
                country_code=country_code,
                locator_domain=base_url,
                hours_of_operation="; ".join(hours),
            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)

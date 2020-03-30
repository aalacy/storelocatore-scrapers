import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    base_url = "https://www.extendedstayamerica.com"
    r = session.get(
        "https://www.extendedstayamerica.com/hotels", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for link in soup.find('table', class_='sm_greytxt').find_all('a'):
        state_url = base_url + link['href']
        r_state = session.get(state_url, headers=headers)
        soup_state = BeautifulSoup(r_state.text, 'lxml')
        for a in soup_state.find('div', class_='links').find_all('a'):
            data_url = base_url + a['href']
            # print(data_url)
            # url = "https://www.extendedstayamerica.com/hotels/al/birmingham"

            payload = "ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24apidns=svc.esa.com&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24aspToken=F8LlmFcAwnNNUWd7HjqXsi%2Bpv8wrL%2FpxcIzLOdRs3xydz0SwgdzbxlFTO%2F3YQDP4XI5AUOHFJf8552cDuCIJfx3CKqezfB5DU9Z5GNnj8UduSaMkq2s9aWs5ikgXbEcSePFsUtZRNiiMjmVKSFqjM%2FFVWLztxfrYkecxJs%2Fzu1U%3D&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24crossVerify=coosdassb1ml454wmnqw3jcds&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24hdbPromoEnd=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24PromoDisplayMode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24hdfEPP=800.804.3724&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24Login_8%24hdfLoginExp=0&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24Login_8%24hdfFindReservationLink=%2Ffind-reserve%2Fmyreservations%2Fdefault.html&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24Login_8%24loginJQLoginBoxTxtEmail=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24Login_8%24loginJQLoginBoxTxtPassword=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24TTTopNav_7%24Login_8%24hdnfailedLoginCount=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextFriday=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextSaturday=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextSunday=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextMonday=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextFriday2=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextSaturday2=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextSunday2=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnextMonday2=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdSearchCompanyCode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdPreviouslySearched=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swhdnMode=APPLY&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnCurrentFNSBal=-1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnEmployeeDaysTillBenifitsEnabled=-1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnNextFNSBal=-1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnCurrACSPromoBal=-1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnNxtACSPromoBal=-1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdStrValidationCheckoutAfterCheckin=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdStrValidationEnterValidCheckoutDate50Weeks=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnPromocodeNotValidBrand=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swhdmPromoCode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidateWeekendDealWarning1=Please+Note%3A+a+Last-Minute+Week-End+Rate+is+only+available+for+stays+that+include+a+Friday+or+Saturday+check-in+and+a+subsequent+Saturday%2C+Sunday%2C+or+Monday+check-out.++Click+OK+if+you+want+to+keep+your+updated+dates+and+not+book+a+Last+Minute+Week-End+Rate.++Or%2C+click+Cancel+and+change+your+stay+dates+to+days+during+which+the+Last-Minute+Week-End+rate+is+available.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidateWeekendDealWarning2=PLEASE+NOTE%3A+Company+codes+cannot+be+combined+with+Special+Last+Minute+Week-End+Rates.+Are+you+sure+you+want+to+use+this+company+code%3F+Click+OK+if+you+want+to+use+your+company+code+and+not+book+the+Last+Minute+Week-End+Rate.+Click+Cancel+if+you+want+to+book+the+Last+Minute+Week-End+Rate+without+your+company+code.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidateWeekendDealWarning3=PLEASE+NOTE%3A+Promotion+codes+cannot+be+combined+with+Special+Last+Minute+Week-End+Rates.++Are+you+sure+you+want+to+use+this+promotion+code%3F++Click+OK+if+you+want+to+use+your+promotion+code+and+not+book+the+Last+Minute+Week-End+Rate.++Click+Cancel+if+you+want+to+book+the+Last+Minute+Week-End+Rate+without+your+promotion+code.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidationEnterCheckinDate=Please+enter+Check-In+date.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidationEnterCheckoutDate=Please+enter+Check-Out+date.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidationEnterValidCheckinDate=Please+enter+a+valid+Check-In+date.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidationEnterValidCheckoutDateWithFormat=Please+enter+a+valid+Check-Out+date+in+the+format+MM%2Fdd%2Fyyyy.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidationEnterValidCheckinDateWithFormat=Please+enter+a+valid+Check-In+date+in+the+format+MM%2Fdd%2Fyyyy.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrValidationEnterValidCheckinDate50Weeks=Please+enter+a+valid+Check-In+date.+Availability+for+dates+more+than+50+weeks+in+the+future+is+not+available+at+this+time.&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrWatermarkEnterDestination=Please+enter+the+destination&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrWatermarkEnterPromoCode=enter+promo+code&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hdnStrWatermarkEnterCorporateCode=enter+corporate+code&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swtxtDestination=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swiDestinationType=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24searchTerms=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swiBrandSearchHidden=True&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swtxtIn=12%2F12%2F2019&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swtxtOut=12%2F13%2F2019&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swddRooms=1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swddAdults=1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swddChildren=0&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swddRate=1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swtxtPromotionCode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24swtxtCompanyCode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hidPlaceId=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24search_10%24hidType=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24hdnHotelId=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24hdnDestination=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24hdniDestination=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24txtIn=12%2F12%2F2019&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24txtOut=12%2F13%2F2019&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24ddRooms=1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24ddAdults=1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24ddChildren=0&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24ddRate_getrate=1&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24txtPromotionCode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24GetRates1%24txtCompanyCode=&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24hdnIsHotelsRateView=false&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24hdnIsPromoPercentageApplied=false&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24hdnIsTTPropertyListingDiscount=false&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24hfAvalableSet=true&ctl00%24ctl00%24ctl00%24ctl00%24cpd%24mtcph%24rtcph%24HotelResultsInfo_9%24HotelResults_13%24hfimghotel=&__VIEWSTATEGENERATOR=CA0B0334&error=&hundredMiles=true"
            headers1 = {
                'Accept': "*/*",
                'Content-type': "application/x-www-form-urlencoded",
                'User-Agent': "PostmanRuntime/7.15.2",
                'Cache-Control': "no-cache",
                'Postman-Token': "bd6219e7-a937-4bfb-8b87-08b368023017,7dd254b7-dc58-4305-8a28-476a359afa22",
                'Host': "www.extendedstayamerica.com",
                'Cookie': "visid_incap_141877=hseOsffmRya0kYxk229Yk3vH8V0AAAAAQUIPAAAAAAA6N8UDXlId2UN0jYEgMuq6; nlbi_141877=qGuZfpAhuifI5WyCjTZbrAAAAAD1M7bTbDYrQijKFZEicyBK; incap_ses_703_141877=6QbaSj1NBnaJItvC+JrBCXvH8V0AAAAA93hXxrhjlCiJJxUBjPw4tQ==; AWSALB=EFwDGmnYW4IxVpG43mjXGudmt2qiLza4wi0cJbHzp3NSx2i9K1guQlJVgN2hc8DLKbmqWCSSTdh1BKsmcYR7zFrSHofKsr7nvJ58Vt8c+n3I9XCwUQ6j1C9RftQZ; ASP.NET_SessionId=wzajpnayeaqwkjbv0hyhl3gq; GDPR=FALSE; GDPRTEMP=FALSE; YieldifyDataToken=3ECCDEC97814ED9E54CC8A4265FDB22C666FAA255B60F4A32284592E66F8918A0086001088BC46220A429758FE0310E1124A01A070DC44314082DF38E587AACA51D1A39B7FE2AF5F",
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "9679",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
            }

            response = requests.request(
                "POST", data_url, data=payload, headers=headers1)
            # loc_data = requests.request(
            #     "POST", data_url, data=payload, headers=headers)
            soup_data = BeautifulSoup(response.text, 'lxml')
            script = soup_data.find(lambda tag: (
                tag.name == "script") and "var pinList" in tag.text)
            json_data = json.loads(script.text.split(
                "var pinList = ")[1].split("};")[0] + "}")
            for loc in json_data["PushPins"]:
                locator_domain = base_url
                latitude = loc['Latitude']
                longitude = loc["Longitude"]
                location_name = loc["HotelName"]
                street_address = loc["Address"]
                city = loc["HotelCity"]
                state = loc["HotelState"]
                zipp = loc["HotelZip"]
                # print(zipp)
                page_url = loc["MinisiteUrl"]
                # print(page_url)
                store_number = loc["HotelId"]
                hours_of_operation = "<MISSING>"
                location_type = "<MISSING>"
                country_code = "US"
                try:
                    phone_tag = session.get(page_url, headers=headers)
                    soup_phone = BeautifulSoup(phone_tag.text, 'lxml')
                    phone = soup_phone.find(
                        'span', {'id': 'cpd_HotelMiniSite_15_lblHotelPhone'}).text.strip()
                    try:
                        hours = list(soup_phone.find(
                            "span", text="Hours of Operation").parent.stripped_strings)
                        hours_of_operation = " ".join(hours).replace(
                            "Hours of Operation", "").strip()
                        # print(hours_of_operation)
                        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                    except Exception as e:
                        hours_of_operation = "<MISSING>"
                        # print(e)
                        # print(page_url)
                        # print("**************************************")

                    # print(phone)
                except:
                    # print(page_url)
                    phone = "<MISSING>"

                # print(phone)
                # print(page_url)
                if "<MISSING>" == hours_of_operation:
                    hours_of_operation = "Open 24 hours a day, seven days a week"

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = ["<MISSING>" if x == "" else x for x in store]
                if store_number in addresses:
                    continue
                addresses.append(store_number)
                # print("data == " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

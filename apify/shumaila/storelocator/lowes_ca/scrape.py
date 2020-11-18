from bs4 import BeautifulSoup
import csv
import string
import re, time, json

from sgrequests import SgRequests

session = SgRequests()
headers = {'authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCIsImtpZCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCJ9.eyJhdWQiOiJmZWNkMjQwMC0zZGU4LTRlYmUtYTFmYS1hOTMxMzhhYjA0ZjgiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC9mMGY3MDVmZi0zZDNlLTRjMjQtODU0Yy02ZDBiMjBiMmIxMGMvIiwiaWF0IjoxNjA1NjMxMzI5LCJuYmYiOjE2MDU2MzEzMjksImV4cCI6MTYwNTYzNTIyOSwiYWlvIjoiRTJSZ1lHQzA4ZHI5ekhtaWlwVzE4dGNOUDUzM0FnQT0iLCJhcHBpZCI6ImI1Nzk0MjJkLTg5ODEtNGM5NC1iZTU5LTI3MDJlNmQ3N2NlZCIsImFwcGlkYWNyIjoiMSIsImlkcCI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0L2YwZjcwNWZmLTNkM2UtNGMyNC04NTRjLTZkMGIyMGIyYjEwYy8iLCJvaWQiOiJjNDlmMGI2YS01OGVkLTRhYzAtYTA5ZC1iOTk3OTYzMDMwYzAiLCJyaCI6IjAuQUFBQV93WDM4RDQ5SkV5RlRHMExJTEt4REMxQ2ViV0JpWlJNdmxrbkF1YlhmTzBTQUFBLiIsInN1YiI6ImM0OWYwYjZhLTU4ZWQtNGFjMC1hMDlkLWI5OTc5NjMwMzBjMCIsInRpZCI6ImYwZjcwNWZmLTNkM2UtNGMyNC04NTRjLTZkMGIyMGIyYjEwYyIsInV0aSI6Im54cktvZWhqUjBpcmpRa2RKbGNmQUEiLCJ2ZXIiOiIxLjAifQ.OEVj-dhw43gWLGDAXyZUvlL7NO_HDvw6VTCNwDlCrBZWNoVdoyhyH6caIm6EJOJIaMO9HGWV_TAAZrLftTjEHHnN-CKI2pObKi3hKVgwONKcaO14ZqvAbyUDb41thJBpz4JjhY6RJFrg5bcCy4Fj7hL8FfXrXzWi9VXwwatkdWGlh6NEqmoXUTTaSgoeo6l4CU_LXK71qaL_VbxMGyf-xWT8lqWg6Dl4gEqgrlzimYuC9w9GVrs3eDVcp9g2vBcTJwAM9k5A99TGacD3AKMSS_Q-JvfB1_1fOBEFhmtKELkoeiv_sJScrheXRUuDeni-8n73JB8HKgJkzmM40MNYWA',
'content-type': 'application/json;charset=utf-8',
'cookie': 'AMCV_5E00123F5245B2780A490D45%2540AdobeOrg%40AdobeOrg=1075005958%7CMCMID%7C26942207825055299167297840857947920342%7CMCOPTOUT-1605349460s%7CNONE%7CvVersion%7C4.4.1; ph_aid=039e7dbf-1313-40bd-6c5f-4060482023eb-31e9e62ab5388-4505ec265cdaf-34a239ba743f2; _gcl_au=1.1.113315060.1605342263; __esi__gatekeeper=%7B%22signal%22%3A56%2C%22events%22%3A11%7D; __esi__user=fea863e3-b092-3428-fcbc-6dcedb0f9573; _fbp=fb.1.1605342264770.985724713; _pin_unauth=dWlkPU1XVXhaR1UxWlRNdFlqRTFOUzAwWmprekxUZ3hZamt0TVROa1pEQXhZMkUyTTJZeA; optimizelyEndUserId=oeu1605342265707r0.3435377181428896; LPVID=k2MjI5NzQ3NDNhYjEwMGRi; sf_vis_sts=; _ga=GA1.2.1079705033.1605342268; _scid=a018cbcd-d5e8-47df-8fee-eaa10416aa07; ipe_v=dd089fb4-bf28-21b1-8191-93fcbaa775c9; _sctr=1|1605294000000; SC_ANALYTICS_GLOBAL_COOKIE=590d7188290741ba91c3d5a95c1866a4|True; _minicart=VisitorId=590d7188-2907-41ba-91c3-d5a95c1866a4; ai_user=wX96m|2020-11-14T13:07:19.710Z; sn=2971OL; akaalb_ca-prod=~op=CA_GCP_EAST_DFLT:CA_GCP_EAST|~rv=25~m=CA_GCP_EAST:0|~os=842a85c4607824f07d21012037f60849~id=48d734d9dacb602cabec39c8d75119a9; AMCVS_5E00123F5245B2780A490D45%40AdobeOrg=1; ipe_s=f46bc7d8-3d93-6d7d-938e-4ba73964e7b4; _gid=GA1.2.1565326184.1605598500; ipe.17331.pageViewedDay=322; ASP.NET_SessionId=4s3s5a0p3agb0p3blg5ewq4u; ApplicationGatewayAffinityCORS=1ad9599f3757d81a8cc101445842a173309738b28c51087ddb02e27ec66a447c; ApplicationGatewayAffinity=1ad9599f3757d81a8cc101445842a173309738b28c51087ddb02e27ec66a447c; __RequestVerificationToken=DOdkTwGPBsYhYMqKNCDQfm0-dscAbjcdea2oSTyfArqYU3_HIi6is_yHnzp7FF0n1soydgs5P1VWWZij-xzQZKUVc2RA0Nuuja0aL5yo6vs1; Oun=2413OL; StoreSource=Cookie; asc=8c4345dc-baff-4f71-a85f-6c20ae0e0b58; gucid=8c4345dc-baff-4f71-a85f-6c20ae0e0b58; ViewedSignUp=%7B%22data%22%3A%7B%22lastUrl%22%3A%22https%3A%2F%2Fwww.lowes.ca%2F%22%7D%7D; LPSID-8130361=iRcaABjOS5-YwqYoPbTkZg; iad_ran=2; AMCV_5E00123F5245B2780A490D45%40AdobeOrg=1075005958%7CMCIDTS%7C18584%7CMCMID%7C81047891408342885444426177192505527087%7CMCAAMLH-1606229300%7C7%7CMCAAMB-1606229300%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1605631700s%7CNONE%7CvVersion%7C4.4.1; s_cc=true; mp_lowes_ca_mixpanel=%7B%22distinct_id%22%3A%20%22175c5daec153c9-06147abf76eb14-230346c-144000-175c5daec1652d%22%2C%22bc_persist_updated%22%3A%201605342260248%7D; __atuvc=9%7C46%2C3%7C47; _uetsid=5cd5675028a711ebbb76a50e2de776b8; _uetvid=cd5915c0265211eb8676e39c624511a2; _derived_epik=dj0yJnU9QVlqWjA4d05DakNtaFRiOWlWNldxUWVMdkVRRDV0Vm4mbj1nUmgxMWp6SUtaazRSYlRVM0dodGZnJm09MSZ0PUFBQUFBRi16NHI0JnJtPTEmcnQ9QUFBQUFGLXo0cjQ; s_ppvl=lca%253Estore-locator%253Estore-directory%2C60%2C36%2C1270%2C1536%2C754%2C1536%2C864%2C1.25%2CP; ipe.17331.pageViewedCount=2; ipe_17331_fov=%7B%22numberOfVisits%22%3A4%2C%22sessionId%22%3A%22f46bc7d8-3d93-6d7d-938e-4ba73964e7b4%22%2C%22expiry%22%3A%222020-12-14T08%3A24%3A30.310Z%22%2C%22lastVisit%22%3A%222020-11-17T14%3A48%3A42.288Z%22%7D; s_sq=%5B%5BB%5D%5D; s_ppv=lca%253Estore-locator%253Estore-directory%2C50%2C50%2C1054%2C1536%2C338%2C1536%2C864%2C1.25%2CP; gpv_pt=store-locator; gpv_pn=lca%3Estore-locator%3Estore-directory; gpv_pss=store; s_vnum=1606762800206%26vn%3D8; s_invisit=true; s_daysFromLastVisit_s=Less%20than%201%20day; RT="z=1&dm=lowes.ca&si=b8273d92-5648-49f1-b448-082ac2d9fc4c&ss=khm3dfrz&sl=0&tt=0&bcn=%2F%2F684fc53b.akstat.io%2F&nu=7d5b927f0c78c5b5bed4ce657ba50e20&cl=48olv"; ak_bmsc=3A5EA2D5E4FE3BC64139DB26CA440E925C7A99149A340000C5FEB35FD639163A~plGMWcJwxqKdlpMeN8EPf5VbeMfgcPoM0+HvwhU4lzHt88KKf/zE2uxmsLjwspHXGNpWDu5nl0uKPLGgCEcOM8aSZvcFQdgwi5FfTm/0XnkP54/gz6PxMsszNMgaBANanedezAcyiF8+MvkJ+NakKVULGGUiqkW38DsPGpPRIT5mKi58BpryMJ2r5hv/n9D63u7FqpZkegMIDmqWWmNswUzka95hgy3/A5kovTk57iBPk=; akavpau_default=1605632024~id=721e56588e8d7723ba90b71d4c98fa2a; bm_sv=DB975344E07D4EB079F9132751D1C000~BZdALrVhO3GkkrkYw5tUDtoFZODD3bCZHu7V0Nc4FkCQ4OG+6ZNKW89w+9c3HTiDepfTTWBxwyhT0htDXwpbnZvVyPf454lChLbAY32PXQ8iZ3eDaQOMDoKgsaAiw3IznM6WV+9aDiIJobAaBb26zA==; s_getNewRepeat=1605631735723-Repeat; s_daysFromLastVisit=1605631735724; s_visit=1605631735727',
'dtqlws': 'true',
'ocp-apim-subscription-key': 'ee52ddc0d6f3439faf85d704b5787d1d',
'referer': 'https://www.lowes.ca/stores',
'sec-fetch-dest': 'empty',
'sec-fetch-mode': 'cors',
'sec-fetch-site': 'same-origin',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'}




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    p = 0
    data = []
    titlelist = []
    pattern = re.compile(r'\s\s+')
    cleanr = re.compile(r'<[^>]+>')
    states = ['Alberta','British Columbia','Manitoba','New Brunswick','Newfoundland and Labrador','Northwest Territories','Nova Scotia','Nunavut','Ontario',
              'Prince Edward Island','Quebec','Saskatchewan','Yukon','N7S%206M8','K2S%200P5','P3B%204K6','M1V%205P7','M8Z 1V1']
    for statenow in states:
        url = 'https://www.lowes.ca/apim/stores?maxResults=4&responseGroup=large&query='+statenow
        loclist = session.get(url,headers=headers).json()       
        for loc in loclist:
            loc = loc['store']
            #print(loc)
            pcode = loc['zip']
            ccode = 'CA'
            street = loc['address']
            longt = loc['long']
            lat = loc['lat']
            phone = loc['phone']
            title = loc['store_name']
            store = loc['id']
            state = loc['state']
            city = loc['city']
            hourlist = loc['storeHours']
            link = 'https://www.lowes.ca/stores/'+loc['bis_name']
            #hourlist = json.loads(hourlist)
            hours = ''
            for hr in hourlist:
                hr = hr['day']
                day = hr['day']
                start = hr['open'].split(':')
                start = ':'.join(start[0:2])
                endtime = (int)(hr['close'].split(':',1)[0])
                if endtime > 12:
                    endtime = endtime - 12
                close = str(endtime)+":00 PM "
                hours = hours + day +' ' +start + ' AM - ' + close
                
            if link in titlelist:
                continue
            
            titlelist.append(link)
            
            data.append([
                        'https://www.lowes.ca/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        ccode,
                        store,
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
            #print(p,data[p])
            p += 1
                
   
           
        
    return data


def scrape():
    data = fetch_data()
    write_output(data)
   

scrape()

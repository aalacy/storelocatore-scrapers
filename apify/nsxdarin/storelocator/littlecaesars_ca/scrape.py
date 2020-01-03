import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'api.cloud.littlecaesars.com',
           'method': 'GET',
           'referer': 'https://littlecaesars.ca/en-ca/stores/search/RichmondHill',
           'accept-language': 'en-ca',
           'cache-control': 'no-cache, max-age=0',
           'origin': 'https://littlecaesars.ca'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

canada = ['Toronto','Montreal','Calgary','Ottawa','Edmonton','Mississauga','Winnipeg','Vancouver','Brampton','Hamilton','Quebec','Surrey','Laval','Halifax','London','Markham','Vaughan','Gatineau','Saskatoon','Longueuil','Kitchener','Burnaby','Windsor','Regina','Richmond','RichmondHill','Oakville','Burlington','GreaterSudbury','Sherbrooke','Oshawa','Saguenay','Levis','Barrie','Abbotsford','Coquitlam','TroisRivieres','StCatharines','Guelph','Cambridge','Whitby','Kelowna','Kingston','Ajax','Langley','Saanich','Terrebonne','Milton','StJohns','ThunderBay','Waterloo','Delta','ChathamKent','RedDeer','StrathconaCounty','Brantford','StJeansurRichelieu','CapeBreton','Lethbridge','Clarington','Pickering','Nanaimo','Kamloops','NiagaraFalls','NorthVancouver','Victoria','Brossard','Repentigny','Newmarket','Chilliwack','MapleRidge','Peterborough','KawarthaLakes','Drummondville','StJerome','PrinceGeorge','SaultSteMarie','Moncton','Sarnia','WoodBuffalo','NewWestminster','StJohn','Caledon','Granby','StAlbert','NorfolkCounty','MedicineHat','GrandePrairie','Airdrie','HaltonHills','PortCoquitlam','Fredericton','Blainville','StHyacinthe','Aurora','NorthVancouver','Welland','NorthBay','Belleville','Mirabel','Shawinigan','DollardDesOrmeaux','Brandon','Rimouski','Chateauguay','Mascouche','Cornwall','Victoriaville','WhitchurchStouffville','HaldimandCounty','Georgina','StEustache','QuinteWest','WestVancouver','RouynNoranda','Timmins','Boucherville','Woodstock','SalaberrydeValleyfield','Vernon','StThomas','Mission','VaudreuilDorion','Brant','Lakeshore','Innisfil','Charlottetown','PrinceAlbert','Langford','BradfordWestGwillimbury','SorelTracy','NewTecumseth','SpruceGrove','MooseJaw','Penticton','PortMoody','WestKelowna','CampbellRiver','StGeorges','ValdOr','CoteStLuc','Stratford','PointeClaire','Orillia','Alma','FortErie','LaSalle','Leduc','SteJulie','NorthCowichan','Chambly','Orangeville','Okotoks','Leamington','StConstant','Grimsby','Boisbriand','Magog','StBrunodeMontarville','ConceptionBaySouth','SteTherese','Langley','Cochrane','Courtenay','ThetfordMines','SeptIles','Dieppe','Whitehorse','PrinceEdwardCounty','ClarenceRockland','FortSaskatchewan','LaPrairie','EastGwillimbury','Lincoln','Tecumseh','MountPearl','Beloeil','LAssomption','Amherstburg','StLambert','Collingwood','Kingsville','BaieComeau','Paradise','Brockville','OwenSound','Varennes','Candiac','StrathroyCaradoc','StLinLaurentides','WasagaBeach','Joliette','Essex','Westmount','MontRoyal','FortStJohn','Kirkland','Cranbrook','WhiteRock','StLazare','Chestermere','Huntsville','CornerBrook','Riverview','Lloydminster(Part)','Yellowknife','Squamish','RiviereduLoup','Cobourg','Beaconsfield','Dorval','StAugustindeDesmaures','Thorold','Camrose','MontStHilaire','PittMeadows','PortColborne','Quispamsis','OakBay','SteMarthesurleLac','SalmonArm','PortAlberni','Esquimalt','Miramichi','NiagaraontheLake','DeuxMontagnes','Beaumont','MiddlesexCentre','StonyPlain','Petawawa','Pelham','StBasileleGrand','SteCatherine','Midland','Colwood','CentralSaanich','PortHope','SwiftCurrent','Edmundston','LAncienneLorette','NorthGrenville','Yorkton','Tracadie','StColomban','Bracebridge','GreaterNapanee','Tillsonburg','Steinbach','SteSophie','Kenora']

def fetch_data():
    ids = []
    for city in canada:
        url = 'https://api.cloud.littlecaesars.com/bff/api/stores?city=' + city
        website = 'littlecaesars.ca'
        print('%s...' % city)
        r = session.get(url, headers=headers)
        for item in json.loads(r.content)['stores']:
            name = "Little Caesar's"
            city = item['address']['city']
            state = item['address']['state']
            country = 'CA'
            add = item['address']['street'] + ' ' + item['address']['street2']
            add = add.strip()
            zc = item['address']['zip']
            lat = item['latitude']
            lng = item['longitude']
            phone = item['phone']
            store = item['storeId']
            typ = item['storeType']
            purl = 'https://order.littlecaesars.com/en-us/stores/' + str(store)
            try:
                hours = item['storeOpenTime'] + '-' + item['storeCloseTime']
            except:
                hours = '<MISSING>'
            if store not in ids:
                ids.append(store)
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

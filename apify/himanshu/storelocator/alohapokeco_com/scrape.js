const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

async function scrape(){
  return new Promise(async (resolve,reject)=>{
    url=`https://www.alohapokeco.com/wp-admin/admin-ajax.php?action=store_search&lat=41.87811&lng=-87.6298&max_results=25&search_radius=25&autoload=1`;
    request(url,async function(err,res,body){
        if(!err && res.statusCode==200){
            var maindata=JSON.parse(res.body);
            var items=[];
            for(const item of maindata)
            {
                var $=cheerio.load(item.hours);
                var hour=$('table tr').eq(0).find('td').eq(0).text()+' : '+$('table tr').eq(0).find('td').eq(1).text()+' , '+$('table tr').eq(1).find('td').eq(0).text()+' : '+$('table tr').eq(1).find('td').eq(1).text()+' , '+$('table tr').eq(2).find('td').eq(0).text()+' : '+$('table tr').eq(2).find('td').eq(1).text()+' , '+$('table tr').eq(3).find('td').eq(0).text()+' : '+$('table tr').eq(3).find('td').eq(1).text()+' , '+$('table tr').eq(4).find('td').eq(0).text()+' : '+$('table tr').eq(4).find('td').eq(1).text()+' , '+$('table tr').eq(5).find('td').eq(0).text()+' : '+$('table tr').eq(5).find('td').eq(1).text()+' , '+$('table tr').eq(6).find('td').eq(0).text()+' : '+$('table tr').eq(6).find('td').eq(1).text();
                items.push({
                    locator_domain: 'https://www.alohapokeco.com/',
                    location_name:item.store,
                    street_address: item.address,
                    city:item.city,
                    state:item.state,
                    zip:item.zip,
                    country_code: 'US',
                    store_number:item.id,
                    phone:item.phone.trim()?item.phone:"<MISSING>",
                    location_type: 'alohapokeco',
                    latitude: item.lat,
                    longitude: item.lng,
                    hours_of_operation:hour
                });
            }
           resolve(items);
            
        }
    });
  })
}
Apify.main(async () => {
    const data = await scrape();
    await Apify.pushData(data);
});

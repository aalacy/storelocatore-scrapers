const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
async function scrape(){
  return new Promise(async (resolve,reject)=>{
      var url = 'http://www.vans.co.in/store-locator/';   
      request(url,(err,res,html)=>{

        if(!err && res.statusCode==200){
       
              const $  =cheerio.load(html);
              var items=[];
      
              var main = $('#markers ').find('ol').find('li').nextAll('li')//.html();
      
              $(main).each(function(i, elem) {
                var lattitude = $(this).attr('data-lat'); 
                var store_number = $(this).attr('data-placeid');
                var location_name = $(this).attr('data-title');
                var longitude =$(this).attr('data-long');
                var raw_address =$(this).attr('data-address-google-maps');
                var hour =$(this).attr('data-opendate');
                var phone = $(this).attr('data-phone').trim();  
                items.push({
                    locator_domain : 'http://www.vans.co.in/',
                    location_name : location_name,
                    raw_address : raw_address,
                    street_address : '<INACCESSIBLE>',
                    city:'<INACCESSIBLE>',
                    state:'<INACCESSIBLE>',
                    zip:'<INACCESSIBLE>',
                    country_code: 'IN',
                    store_number:store_number,
                    phone:phone,
                    location_type:'vans',
                    latitude:lattitude,  
                    longitude :longitude,
                    hours_of_operation:hour 
                });  
             });
             resolve(items)
      
         }
      });
      
  })
}
Apify.main(async () => {
    
    const data = await scrape();
    await Apify.pushData(data);
});

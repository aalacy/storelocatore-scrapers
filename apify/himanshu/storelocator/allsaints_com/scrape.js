const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
const zipcode=require('zipcodes')
const { getCode,getName } = require('country-list');
async function scrape(){
  return new Promise(async (resolve,reject)=>{
      var url=`https://store-locator-api.allsaints.com/shops?attributes=`;
      request(url,async function(err,res,re){
          if(!err && res.statusCode==200){
            var maindata=JSON.parse(res.body);
            var items=[];
            var totpage=maindata.length;
            var page=0;
            for(const item1 of maindata)
            {    
                var url1="https://store-locator-api.allsaints.com/"+item1.country_slug+"/"+item1.city_slug+"/"+item1.slug;
                request(url1,async function(err1,res1,re1){
                    page++;
                    if(!err1 && res1.statusCode==200){
                        var item=JSON.parse(res1.body);
                        var hour="<MISSING>";
                        if(item.opening_hours.Monday[0].open!=null){
                           hour= "Monday : "+item.opening_hours.Monday[0].open+" - "+item.opening_hours.Monday[0].close;
                           hour+= " Tuesday : "+item.opening_hours.Tuesday[0].open+" - "+item.opening_hours.Tuesday[0].close;
                           hour+= " Wednesday : "+item.opening_hours.Wednesday[0].open+" - "+item.opening_hours.Wednesday[0].close;
                           hour+= " Thursday : "+item.opening_hours.Thursday[0].open+" - "+item.opening_hours.Thursday[0].close;
                           hour+= " Friday : "+item.opening_hours.Friday[0].open+" - "+item.opening_hours.Friday[0].close;
                           hour+= " Saturday : "+item.opening_hours.Saturday[0].open+" - "+item.opening_hours.Saturday[0].close;
                           if(item.opening_hours.Sunday[0].open && item.opening_hours.Sunday[0].close){
                            hour+= " Sunday : "+item.opening_hours.Sunday[0].open+" - "+item.opening_hours.Sunday[0].close;
                           }
                           else{
                            hour+= " Sunday : closed";
                           }
                        }
                        item.opening_hours
                        var address=item.address_line1;
                        if(item.address_line2 && item.address_line2!=null)
                          address+=' '+item.address_line2;
                        if(item.address_line3 && item.address_line3!=null)  
                          address+=' '+item.address_line3;
                        
                        address=address.trim();
                        var country=await getCode(item.country);
                        if(item.country=="USA"){
                            country="US";
                        }
                        var zip=item.post_code.trim(); 
                        var state="";
                        if(country=="US"){
                            var data=item.post_code.split(' ');
                            if(data.length==2){
                                zip=data[1].trim();
                                state=data[0].replace(',',' ').trim();
                            }
                        }
                        var flag=0;
                        if(item.country=="Canada"){
                            var data1=item.post_code.split(' ');
                            if(data1.length==3){
                                zip=data1[1]+' '+data1[2].trim();
                            }
                            var hills = zipcode.lookup(zip);
                            state=hills.state.toLowerCase();
                            var str=/^[ABCEGHJ-NPRSTVXY][0-9][ABCEGHJ-NPRSTV-Z] [0-9][ABCEGHJ-NPRSTV-Z][0-9]$/;
                            if(!zip.match(str)){
                                flag=1;
                            }
                        }
                        if(flag==0){
                            items.push({
                                locator_domain: 'https://www.allsaints.com/',
                                location_name:item.name,
                                street_address: address,
                                city:item.city,
                                state:state?state:'<MISSING>',
                                zip:zip,
                                country_code:country?country:item.country,
                                store_number:'<MISSING>',
                                phone:item.phone_number,
                                location_type: 'allsaints',
                                latitude: item.coordinates.latitude,
                                longitude: item.coordinates.longitude,
                                hours_of_operation:hour
                            });
                        }
                        if(totpage==page){
                            resolve(items);
                        }
                    }
                    
                });
               
            }
          }
      })
  })
}
Apify.main(async () => {
    
    const data = await scrape();
    await Apify.pushData(data);
});

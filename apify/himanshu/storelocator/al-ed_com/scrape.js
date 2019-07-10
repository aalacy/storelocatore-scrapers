const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

async function scrape(){
  return new Promise(async (resolve,reject)=>{
      var url=`https://al-ed.com/storelocator/index/loadstore?curPage=1`;
      request(url,async function(err,res,re){
          if(!err && res.statusCode==200){
              var main=JSON.parse(res.body);
              var totpage=main.num_store;
              var page=0;
              var r=Math.ceil(main.num_store/10);
              var items=[];
              for(k=1;k<=r;k++){
                  url=`https://al-ed.com/storelocator/index/loadstore?curPage=`+k;
                  request(url,async function(err,res,re){
                      if(!err && res.statusCode==200){
                          var main=JSON.parse(res.body);
                          var detail=main.storesjson;
                          for(const item of detail){
                             
                              url=`https://al-ed.com/`+item.rewrite_request_path;
                              await request(url,function(err1,res1,body){

                                  if(!err && res.statusCode==200){
                                      var $=cheerio.load(body);
                                      var address=item.address;
                                      var state="";
                                      var city="";
                                      var q=address.lastIndexOf(' ');
                                      var zip=address.substr(q+1,)
                                      // var zip="";
                                      var madd=item.address.split(',');
                                      if(madd.length==2){
                                          address=madd[0];
                                          state=madd[1].trim().split(' ')[0];
                                          zip=madd[1].trim().split(' ')[1];
                                      }
                                      else if(madd.length==3){
                                          address=madd[0];
                                          city=madd[1].trim();
                                          state=madd[2].trim().split(' ')[0];
                                          zip=madd[2].trim().split(' ')[1];
                                      }
                                      var hour="Sunday : "+$('#open_hour table tbody tr').eq(0).find('td').eq(2).text()+
                                               " , Monday : "+$('#open_hour table tbody tr').eq(1).find('td').eq(2).text()+
                                               " , Tuesday : "+$('#open_hour table tbody tr').eq(2).find('td').eq(2).text()+
                                               " , Wednesday : "+ $('#open_hour table tbody tr').eq(3).find('td').eq(2).text()+
                                               " , Thurday : "+$('#open_hour table tbody tr').eq(4).find('td').eq(2).text()+
                                               " , Friday : "+$('#open_hour table tbody tr').eq(5).find('td').eq(2).text()+
                                               " , Saturday : "+$('#open_hour table tbody tr').eq(6).find('td').eq(2).text();
                                      var regexp = /^[0-9]+$/;
                                      if(zip.match(regexp))
                                        items.push({
                                    locator_domain: 'https://al-ed.com',
                                    location_name:item.store_name,
                                    street_address: "<INACCESSIBLE>",
                                    raw_address:address,
                                    city:city?city:"<INACCESSIBLE>",
                                    state:state?state:"<INACCESSIBLE>",
                                    zip:zip?zip:"<INACCESSIBLE>",
                                    country_code: 'US',
                                    store_number:item.storelocator_id,
                                    phone:item.phone,
                                    location_type: 'al-ed',
                                    latitude: item.latitude,
                                    longitude: item.longitude,
                                    hours_of_operation:hour
                                        });
                                      page++;
                                      if(totpage==page){
                                          resolve(items);
                                      }

                                  }
                              });
                              
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

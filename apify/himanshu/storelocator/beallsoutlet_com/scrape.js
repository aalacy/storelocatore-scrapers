const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');
async function scrape(){
  return new Promise(async (resolve,reject)=>{
      var url=`https://stores.beallsoutlet.com/`;
      request(url,function(err,res,body){
          if(!err && res.statusCode==200){
            var $=cheerio.load(body);
            var main=$('.no-results').children('.map-list-item-wrap.is-single');
            // console.log(main.length);
            var items=[];           
            function mainhead(i)
            {
                if(main.length>i)
                {
                    var url1=main.eq(i).find('a').attr('href');
                    request(url1,function(err1,res1,body1){
                        if(!err1 && res1.statusCode==200){
                            var $1=cheerio.load(body1);
                            var main1=$1('.map-list').children('.map-list-item-wrap.is-single');
                            function mainhead1(i1){
                                if(main1.length>i1)
                                {
                                    var url2=main1.eq(i1).find('a').attr('href');
                                    request(url2,function(err2,res2,body2){
                                        if(!err2 && res2.statusCode==200){
                                            var $2=cheerio.load(body2);
                                            var main2=$2('.locator .map-list').children('.map-popup-item-wrap');
                                            function mainhead2(i2){
                                                if(main2.length>i2)
                                                {
                                                    var head=main2.eq(i2).find('.map-list-item-header a').attr('title');
                                                    var k=head.lastIndexOf(' ');
                                                    var store=head.substr(k,).trim();
                                                    var name=head.substr(0,k).trim();
                                                    var address=main2.eq(i2).find('.address span').eq(0).text().trim();
                                                    var madd=main2.eq(i2).find('.address span').eq(1).text().trim();
                                                    var city=madd.split(',')[0];
                                                    var mstat=madd.split(',')[1].trim();
                                                    var state=mstat.split(' ')[0].trim();
                                                    var zip=mstat.split(' ')[1].trim();
                                                    var mainhour=main2.eq(i2).find('.hours-wrapper .hours .day-hour-row');
                                                    var hour="<MISSING>";
                                                    var d=JSON.parse(main2.eq(i2).find('.hours-wrapper').html().toString().replace('<!--','').replace('-->',''));
                                                    hour= "Monday : "+d.days.Monday[0].open+"-"+d.days.Monday[0].close;
                                                    hour+= " Tuesday : "+d.days.Tuesday[0].open+"-"+d.days.Tuesday[0].close;
                                                    hour+= " Wednesday : "+d.days.Wednesday[0].open+"-"+d.days.Wednesday[0].close;
                                                    hour+= " Thursday : "+d.days.Thursday[0].open+"-"+d.days.Thursday[0].close;
                                                    hour+= " Friday : "+d.days.Friday[0].open+"-"+d.days.Friday[0].close;
                                                    hour+= " Saturday : "+d.days.Saturday[0].open+"-"+d.days.Saturday[0].close;
                                                    hour+= " Sunday : "+d.days.Sunday[0].open+"-"+d.days.Sunday[0].close;
                                                    var phone=main2.eq(i2).find('.phone').text().trim();
                                                    items.push({
                                                        locator_domain: 'https://www.beallsoutlet.com/',
                                                        location_name:name?name:'<MISSING>',
                                                        street_address:address?address:'<MISSING>',
                                                        city:city?city:'<MISSING>',
                                                        state:state?state:'<MISSING>',
                                                        zip:zip?zip:'<MISSING>',
                                                        country_code:"US",
                                                        store_number:store?store:'<MISSING>',
                                                        phone:phone?phone:'<MISSING>',
                                                        location_type: 'beallsoutlet',
                                                        latitude:'<MISSING>',
                                                        longitude:'<MISSING>',
                                                        hours_of_operation:hour
                                                    });
                                                    mainhead2(i2+1);
                                                }
                                                else{
                                                     mainhead1(i1+1);
                                                }
                                            }
                                            mainhead2(0);
                                        }   
                                    });
                                }
                                else{
                                    mainhead(i+1);
                                }
                            }
                            mainhead1(0);
                        }   
                    });
                }
                else{
                    resolve(items);
                }
            }
            mainhead(0);
          }
      })
  })
}
Apify.main(async () => {
    
    const data = await scrape();
    await Apify.pushData(data);
});
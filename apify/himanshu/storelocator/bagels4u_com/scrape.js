const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://www.bagels4u.com/locations';

 
 
async function scrape(){
  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{
                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                          var unique=[];
                          var items=[];

                          var main = $('#ma4c9inlineContent-gridContainer').find('.txtNew');

                          

                          function mainhead(i)

                          {
                              if(main.length>i)

                                  {

                            
                                     
                            var tmp = main.eq(i).children('p');
                            
                            var location_name =  main.eq(i).find('p:nth-child(1)').text().replace('Bagels-4-U','').replace('of ','').trim(); 
                           if(tmp.length == 5){
                               
                              var address = main.eq(i).find('p:nth-child(2)').text().replace('Pheasant Run Plaza','177 Washington Valley Road').trim();
                              var state_tmp = main.eq(i).find('p:nth-child(4)').text().replace('Tel.: (908) 359-2100','Hillsborough, NJ 08876').replace('Tel.: (908) 927-9988','North Branch, NJ 07936');
                              var state_tmp1 =state_tmp.split(',');
                              var city = state_tmp1[0];
                              var state_tmp2 = state_tmp1[1];
                              var state_tmp3 =  state_tmp2.split(' ');
                              var state = state_tmp3[1];
                              var zip = state_tmp3[2];
                              
                               
                              var phone = main.eq(i).find('p:nth-child(4)').text().replace('Warren, NJ 07060','(732) 469-5829').replace('Tel.:','').trim();
                            }

                            else if(tmp.length == 4){
                              
                              var address = main.eq(i).find('p:nth-child(2)').text().replace('601 Boulevard','601 Boulevard Kenilworth').trim();
                              var state_tmp = main.eq(i).find('p:nth-child(3)').text();
                              var state_tmp1 =state_tmp.split(',');
                              var city = state_tmp1[0];
                              var state_tmp2 = state_tmp1[1];
                              var state_tmp3 =  state_tmp2.split(' ');
                              var state = state_tmp3[1];
                              var zip = state_tmp3[2];
                              var phone = main.eq(i).find('p:nth-child(4)').text().replace('Tel.:','').trim();
                              
                         }
                            else if(tmp.length ==  6){
                            
                              var address = main.eq(i).find('p:nth-child(2)').text().replace('Bernardsville Plaza Shopping',' 80 Morristown Rd. Store 1').trim();
                              var state_tmp = main.eq(i).find('p:nth-child(3)').text().replace('80 Morristown Rd. Store 1','Bernardsville, NJ 07924');
                              var state_tmp1 =state_tmp.split(',');
                              var city = state_tmp1[0];
                              var state_tmp2 = state_tmp1[1];
                              var state_tmp3 =  state_tmp2.split(' ');
                              var state = state_tmp3[1];
                              var zip = state_tmp3[2];
                              var phone = main.eq(i).find('p:nth-child(4)').text().replace('Bernardsville, NJ 07924','(908) 221-0080').replace('Tel.:','').trim();
                            }
                            if(location_name!== 'Headquarters'){
                             
                              items.push({  

                                locator_domain: 'https://www.bagels4u.com/', 

                                location_name: location_name, 
                    
                                street_address: address,
                    
                                city: city, 
                    
                                state: state,
                    
                                zip:  zip,
                    
                                country_code: 'US',
                    
                                store_number: '<MISSING>',
                    
                                phone: phone,
                    
                                location_type: '<MISSING>',
                    
                                latitude: '<MISSING>',
                    
                                longitude: '<MISSING>', 
                    
                                hours_of_operation: '<MISSING>',
                                
                                page_url:'<MISSING>'});
                            }
                              

                               
                            
                            
                                       
                            mainhead(i+1);
                              
                          }
                                
                                
                          else{
                      
                          resolve(items);
                      
                          }
                    } 
  
                    mainhead(1);   
  }
 
 });
})
}
  
Apify.main(async () => {

    

    const data = await scrape();
    
    await Apify.pushData(data);
   
    
  
  });

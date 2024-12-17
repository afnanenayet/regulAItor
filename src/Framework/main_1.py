# main.py

import asyncio
from agents.conversation_workflow import conversation_workflow
from agents.agent_manager import group_chat


import logging


async def main():
    # Manually provide the warning letter and template
    warning_letter = """\
Delivery Method: 
        VIA UPS and Electronic Mail
                                                                                                                                                                                                                                                                                                                                                                                                                              
      
              Reference #: 
        RW2402159
      
              Product: 
        Tobacco                          
            
            
            
            
            
            
            
             
            
            
            
              
            
            
            
      
          
              





  
    

        Recipient:

                      
  
    Recipient Name
              Troy Duncan and Lilia Ahmed
          

                    
            1 Stop Supply Corp. dba 1 Stop Vapor Supply

          
                      4610 S May Ave
Oklahoma City, OK 73119-6404
United States
          
          
            
            

     sales@1stopvapor.com 

          
    
              

       
    
          
          Issuing Office:
        
         
          Center for Tobacco Products
        
         
          United States
        
        
        
        
        
    
     
      
    
    
      


 

 



June 12, 2024

WARNING LETTER

Dear Troy Duncan and Lilia Ahmed:

The Center for Tobacco Products of the U.S. Food and Drug Administration (FDA) recently reviewed the website https://1stopvapor.com and determined that electronic nicotine delivery system (ENDS) and e-liquid products listed there are offered for sale or distribution to customers in the United States.

Under section 201(rr) of the Federal Food, Drug, and Cosmetic Act (FD&C Act) (21 U.S.C. § 321(rr)), these products are tobacco products because they are made or derived from tobacco or contain nicotine from any source and intended for human consumption. Certain tobacco products, including ENDS and e-liquid products, are subject to FDA jurisdiction under section 901(b) of the FD&C Act (21 U.S.C. § 387a(b)) and 21 C.F.R. § 1100.1, and are required to be in compliance with the requirements in the FD&C Act.

Please be aware that, on March 15, 2022, the President signed legislation to amend the FD&C Act to extend FDA’s jurisdiction to products “containing nicotine from any source,” not just nicotine derived from tobacco. See Consolidated Appropriations Act, 2022, Public Law 117-103, Division P, Title I, Subtitle B. Specifically, this legislation expanded the definition of “tobacco product” under section 201(rr) of the FD&C Act (21 U.S.C. § 321(rr)) to include products containing nicotine from any source. Tobacco products, including ENDS and e-liquid products, containing nicotine from any source, must be in compliance with the FD&C Act and its implementing regulations. For more information, please see https://www.fda.gov/tobacco-products/ctp-newsroom/requirements-products-made-non-tobacco-nicotine-take-effect-april-14.

Generally, to be legally marketed in the United States, the FD&C Act requires “new tobacco products” to have a premarket authorization order in effect. A “new tobacco product” is any tobacco product that was not commercially marketed in the United States as of February 15, 2007, or any modified tobacco product that was commercially marketed after February 15, 2007 (section 910(a) of the FD&C Act; 21 U.S.C. § 387j(a)). Generally, a marketing authorization order under section 910(c)(1)(A)(i) of the FD&C Act (21 U.S.C. § 387j(c)(1)(A)(i)) is required for a new tobacco product unless (1) the manufacturer of the product submitted a report under section 905(j) of the FD&C Act (21 U.S.C. § 387e(j)) and FDA issues an order finding the product substantially equivalent to a predicate tobacco product (section 910(a)(2)(A) of the FD&C Act) or (2) the manufacturer submitted a report under section 905(j)(1)(A)(ii) of the FD&C Act (21 U.S.C. § 387e(j)(1)(A)(ii)) and all modifications are covered by exemptions from the requirements of substantial equivalence granted by FDA under section 905(j)(3) of the FD&C Act (21 U.S.C. § 387e(j)(3)).

New Tobacco Products Without Required Marketing Authorization are Adulterated and Misbranded

FDA has determined that you offer for sale or distribution to customers in the United States ENDS and e-liquid products that lack a marketing authorization order: Cereal Trip - Bad Drip Lab 60mL – 3mg, Don’t Care Bear by Bad Drip Labs 60ml – 3mg, and Funky Republic Ti7000 Smart Disposable - Blue Red Mint.

The tobacco products listed above are new tobacco products because they were not commercially marketed in the United States as of February 15, 2007. These products do not have FDA marketing authorization orders in effect under section 910(c)(1)(A)(i) of the FD&C Act and are not otherwise exempt from the marketing authorization requirement. Therefore, these products are adulterated under section 902(6)(A) of the FD&C Act (21 U.S.C. § 387b(6)(A)). In addition, they are misbranded under section 903(a)(6) of the FD&C Act (21 U.S.C. § 387c(a)(6)) because a notice or other information respecting these products was not provided as required by section 905(j) of the FD&C Act (21 U.S.C. § 387e(j)).

Additional Considerations

FDA finds some of these products particularly concerning because the design of the Bad Drip Labs e-liquid products (see Exhibits A) are likely to appeal to youth by imitating a prescription pill bottle (see Exhibits B). Specifically, the overall presentation of the e-liquid products, including the graphical elements on their labeling and/or advertising, makes it appear that the products are a prescription and could reasonably result in a child or adult ingesting the products. Further, the products are likely to appeal to youth because they enable youth to conceal a tobacco product from parents, teachers, or other adults. FDA is concerned about the rising youth appeal and dramatic rise in youth use of e-liquid products. Any efforts to entice youth to use tobacco products are of concern to FDA. Sales of such unauthorized tobacco products are prohibited, and FDA is concerned that your actions likely encourage unlawful sales, maintain or increase youth use, and contribute to the public health and safety concerns associated with e-liquid products.

  




  




Conclusion and Requested Actions

FDA has determined that your firm markets new tobacco products in the United States that lack premarket authorization. All new tobacco products on the market without the statutorily required premarket authorization are marketed unlawfully and are subject to enforcement action at FDA’s discretion.

For a list of products that received marketing granted orders, please visit our website: https://www.fda.gov/tobacco-products/market-and-distribute-tobacco-product/tobacco-products-marketing-orders#PMTAView%20all%20marketing%20granted.

It is your responsibility to ensure that all tobacco products you sell and/or distribute in the United States and all related labeling and/or advertising on any websites or other media (such as e-commerce, social networking, or search engine websites), and in any retail establishments in which you advertise, comply with each applicable provision of the FD&C Act and FDA’s implementing regulations. Failure to address any violations of the FD&C Act, 21 U.S.C. § 301 et seq. or its implementing regulations relating to tobacco products including the tobacco regulations in 21 C.F.R. Parts 1140, 1141, or 1143, may lead to regulatory action, including, but not limited to, civil money penalties, seizure, and/or injunction. However, this Warning Letter does not constitute “written notice” for purposes of section 303(f)(9)(B)(i)(II) of the FD&C Act. Please note that tobacco products offered for import into the United States that appear to be adulterated and/or misbranded may be detained or refused admission.

The violations discussed in this letter do not necessarily constitute an exhaustive list. You should take prompt action to address any violations that are referenced above and take any necessary actions to bring these tobacco products into compliance with the FD&C Act.

Please submit a written response to this letter within 15 working days from the date of receipt describing your actions to address any violations and bring these products into compliance, including the dates on which you discontinued the violative sale, and/or distribution of these tobacco products and your plan for maintaining compliance with the FD&C Act. If you believe that these products are not in violation of the FD&C Act, include your reasoning and any supporting information for our consideration. This letter notifies you of our findings and provides you with an opportunity to address them. You can find the FD&C Act through links on FDA’s homepage at
http://www.fda.gov.

Please note your reference number, RW2402159, in your response and direct your response via email at CTPCompliance@fda.hhs.gov and to the following address:

DPAL-WL Response, Office of Compliance and Enforcement
FDA Center for Tobacco Products
c/o Document Control Center
Building 71, Room G335
10903 New Hampshire Avenue
Silver Spring, MD 20993-0002

If you have any questions about the content of this letter, please contact CTPCompliance@fda.hhs.gov.

Sincerely,
/S/

Jill Atencio
Acting Director
Office of Compliance and Enforcement
Center for Tobacco Products

VIA UPS and Electronic Mail

cc:

1 Stop Vapor
2809 SW 44th Street
Oklahoma City, OK 73119

GoDaddy.com, LLC
abuse@godaddy.com

Bigcommerce Inc.
abuse@bigcommerce.com
"""

    template = """\

[[DATE]] 



[DISTRICT DIRECTOR NAME]
District Director
[NAME] District Office
U.S. Food and Drug Administration
District Address
City, State  Zip
	Re:	[FIRM NAME]
Initial Response to the 
[DATE] Inspectional Observations (FDA-483)



Dear [DD NAME],

On [DATE], U.S. Food and Drug Administration (FDA) Investigators concluded an inspection of the [COMPANY] (hereafter referred to as “[SHORT NAME]” or the “company”) facility located in [CITY, STATE] and issued Inspectional Observations on the form FDA-483.  We provide our initial response below.  We plan to submit our next update report to FDA on or before [MONTH DAY, YEAR], followed by monthly updates until quarterly updates become more appropriate. 

We recognize and take seriously the significance of the observations in the FDA-483, and are committed to taking all actions necessary to ensure that our systems are in compliance with FDA requirements, and that our products are safe and effective.  As is described in our detailed response below, in addition to correcting the specific items listed in the FDA-483, we have taken and are continuing to take actions to address systemic issues.

In Appendix 1, “Response to the FDA-483 dated [DATE],” we describe our completed and planned actions.  To facilitate review, the FDA-483 observations are italicized, followed by our response in regular font.  Supporting documents relating to actions we have already taken are listed in Appendix 2 “List of Attachments.” Appendix 3, “Table of Actions,” is a comprehensive list of the completed and planned actions relating to each FDA-483 Observation.


Next we highlight some of the activities underway to demonstrate our commitment to driving improvements, not only to the specific areas found in the inspection, but to the business as a whole.  The following are just a few examples:

	[EXAMPLE 1]
	[EXAMPLE 2]

We consider the information contained in this letter and its attachments to be confidential commercial information and not subject to disclosure under the Freedom of Information Act.  Accordingly, we have designated this letter and its attachments as confidential.
 
[I would welcome the opportunity to meet with you to discuss the progress made to date and the planned actions outlined in the attached response.]  [I welcome the opportunity to discuss the progress made to date and the planned actions outlined in the attached response.]  In the meantime, should you have any questions, please contact me at the telephone number: [COMPANY CONTACT PHONE].


Respectfully,



[COMPANY CONTACT]
[TITLE]
[COMPANY NAME]
[CITY, STATE]

Appendices

1.  Response to FDA-483 
2.  List of Attachments
3.  Table of Actions

 
In this section, [COMPANY] lists the Warning Letter items and the text of the FDA-483 Observations in italic font type, and the actions completed and planned follow in regular font.  Appendix 2, “List of Attachments,” contains the supporting documents related to the completed and planned actions outlined in our responses.   

FDA Observation 1

Copy observation verbatim, including annotation, if any.

Response:	  

Completed Actions:  	  
 
On [MONTH DAY, YEAR, COMPANY [STATE COMPLETED ACTION]].  See Appendix 2, Attachment XX for a copy of the [DESCRIBE RECORDS] records. 
On [MONTH DAY, YEAR, COMPANY [STATE COMPLETED ACTION]].  See Appendix 2, Attachment XX for a copy of the [DESCRIBE RECORDS] records. 
  

Planned Actions:	By [MONTH DAY, YEAR, COMPANY] will [DESCRIBE PLANNED ACTIONS].
By [MONTH DAY, YEAR, COMPANY] will [DESCRIBE PLANNED ACTIONS]. 
[COMPANY] also plans to complete [DESCRIBE RECORDS] by [MONTH DAY, YEAR].
[COMPANY] considers this item to be closed.





FDA Observation 2

Copy observation verbatim, including annotation, if any.

Response:	  

Completed Actions:  	  
Planned Actions:	


 
Appendix 2 - List of Attachments
Attachment	Title/Description	Number of pages
1.		
2.		
3		



 

Appendix 3	TABLE OF ACTIONS 

[date] -FDA-483

ACTIONS
	Completed Actions	Planned Actions
FDA-483 Observation 1		
FDA-483 Observation 2		
FDA-483 Observation 3		
FDA-483 Observation 4		
FDA-483 Observation 5		
FDA-483 Observation 6		
FDA-483 Observation 7		
FDA-483 Observation 8		
FDA-483 Observation 9		
FDA-483 Observation 10		
EXAMPLE TEXT	Provided the procedure entitled, “Title”, ***. 
Completed the complaint investigation, ***.
We consider this item to be closed.


"""
    group_chat.context = {
        "warning_letter": warning_letter,
        "template": template
    }

    # Run the conversation workflow
    result = await conversation_workflow(group_chat)

    # Print the result
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
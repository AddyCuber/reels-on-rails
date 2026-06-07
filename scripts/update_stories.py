"""
Update stories.json: rewrite 8 existing stories (villain-first formula) + append 15 new ones.
Run once: python scripts/update_stories.py
"""

import json
from pathlib import Path

STORIES_FILE = Path("stories.json")

# ─────────────────────────────────────────────────────────────────────────────
# 8 REWRITES  (keyed by id — will replace matching entry in stories list)
# ─────────────────────────────────────────────────────────────────────────────
REWRITES = {

"story_001": {
  "id": "story_001",
  "title": "My Brother Stole Her Will",
  "genre": "family_betrayal",
  "hook": "My brother told our dying mother I was stealing from her. He had the bank statements to prove it. They were fake.",
  "card_text": '"She\'s been draining your accounts. I have the statements." That\'s what my brother told our dying mother. So I opened the vase she left me. What I found sent him to trial.',
  "narration": (
    '"She\'s been draining your accounts. I have the statements." That was what my brother Dominic told our mother in the winter of her final year. '
    "I found out because she wrote it down.\n\n"
    "She mailed herself a letter — notarized, dated, sealed inside the ceramic vase she had kept on the mantle since I was a child. "
    "Her instructions to the estate attorney were specific: give the vase to me, unopened, the day after the reading.\n\n"
    "I sat in that office and listened while Dominic received the house, two hundred and eighty thousand in savings, the car, the jewelry. "
    "I received the vase. He did not look up from his phone when they read my portion.\n\n"
    "I drove home. I put the letter on the kitchen table and read it twice. Then I opened the vase.\n\n"
    "There was a flash drive inside. One folder, labeled with my name.\n\n"
    "A forensic accountant reviewed the files within four days. The bank statements Dominic had shown our mother were fabricated. "
    "The logos were wrong. The account numbers did not match any statements our bank had issued in the prior decade. "
    "The formatting inconsistencies alone would have flagged them immediately to anyone who looked carefully. "
    "Our mother had not looked carefully. She was eighty-one and frightened and Dominic had been very convincing.\n\n"
    "The real records showed no unauthorized withdrawals by me. "
    "The real records also showed sixty-three thousand dollars transferred from our mother's savings over eighteen months, "
    "every transfer authorized by a power of attorney Dominic had obtained by telling her attending physician I was incapacitated.\n\n"
    "I did not call Dominic. I called the district attorney's office.\n\n"
    "He was charged with elder financial abuse, forgery, and fraud. "
    "The will was contested on grounds of undue influence and fraudulent misrepresentation. "
    "Six months after the contest was filed, the court overturned it. "
    "Our mother's original will — the one from four years prior — was reinstated. The estate passed to me.\n\n"
    "His attorney called twice. Both times the offer was full repayment in exchange for dropping the charges. "
    "I declined both times and did not explain why.\n\n"
    "I moved into my mother's house the month probate closed. "
    "I use her plates on Sundays. I keep the vase on the same mantle where she always kept it. "
    "Some mornings I sit at her kitchen table with coffee and read the newspaper the way she used to before she stopped being well enough to drive.\n\n"
    "The district attorney's office tells me the case is proceeding. I have given my statement and produced every document they asked for.\n\n"
    "Dominic's trial is scheduled for spring.\n\n"
    "She knew something was wrong. She left me the evidence and trusted me to know what to do with it.\n\n"
    "I did."
  ),
  "broll_keywords": ["legal documents", "kitchen table", "old photographs", "courthouse exterior", "family home"],
  "hashtags": ["shorts", "storytime", "familydrama", "betrayal", "inheritance", "drama"],
  "description": "My brother told our dying mother I was stealing from her. She hid the truth inside a vase and left it for me to find.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_002": {
  "id": "story_002",
  "title": "Sue Me",
  "genre": "neighbor_drama",
  "hook": "My neighbor built his fence two feet into my yard. When I showed him the survey he told me to sue him. I want to be clear that I did.",
  "card_text": '"What are you going to do about it, get a lawyer?" That\'s what Greg said when I showed him the survey. So I filed a claim and reported three code violations the same afternoon. He tore the fence down himself, in the rain.',
  "narration": (
    '"What are you going to do about it, get a lawyer?" Greg said that to me on a Tuesday morning in October, still in his bathrobe, '
    "with the survey in his hand. He looked at it for four seconds, smiled, and closed the door.\n\n"
    "I went home and made a phone call.\n\n"
    "I had lived on Alderton Street for eleven years. Greg had moved in eight months before. "
    "In those eight months his dog had destroyed my garden gate, he had parked across my driveway twice, "
    "and he had built a six-foot fence along what he believed was our shared property line. "
    "It wasn't. The fence sat twenty-six inches inside my yard and blocked the only side-gate access to my backyard from the driveway.\n\n"
    "I had the original survey from when I purchased the house. The measurements were not ambiguous.\n\n"
    "My attorney filed the property encroachment claim that week. While she was doing that I submitted the fence separately to the city building department. "
    "Three violations: exceeded the height limit for side-yard structures, failed the required setback, no building permit had ever been pulled. "
    "I filed those myself that same afternoon. It took forty minutes.\n\n"
    "The city issued a notice of violation within ten days. Greg had fourteen days to remove the fence or face daily fines of two hundred and fifty dollars per day.\n\n"
    "He called me to negotiate. I let it go to voicemail.\n\n"
    "The encroachment lawsuit settled four months after filing. Greg paid eleven thousand dollars in legal fees and costs. "
    "He also removed the fence himself — his contractor had already refused to return after the citation.\n\n"
    "He did it on a Saturday in November. It was raining. I could see him from the porch through the kitchen window. "
    "I made coffee and read until he was done. It took most of the afternoon. He did not ask for help.\n\n"
    "The house went on the market six weeks later. I found out from a neighbor who saw the listing.\n\n"
    "The couple who bought it knocked on my door on their move-in day with cookies from a bakery downtown. "
    "They asked if I knew why the previous owner had left so quickly. "
    "I said I was not entirely sure.\n\n"
    "They invited me to their housewarming. I went.\n\n"
    "Some people think they can outlast you by being unpleasant. What they miss is that unpleasantness and legal exposure are not the same thing. "
    "Greg was prepared to be difficult. He was not prepared for the city building department.\n\n"
    "My side gate works fine. The garden has mostly grown back. "
    "The new neighbors have a dog that has never touched my fence."
  ),
  "broll_keywords": ["wooden fence", "suburban house", "rainy street", "coffee morning", "garden flowers"],
  "hashtags": ["shorts", "storytime", "neighbordrama", "justice", "revenge", "drama"],
  "description": "He told me to sue him. I filed the claim and three code violations the same afternoon. He tore it down himself in the rain.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_003": {
  "id": "story_003",
  "title": "The Caregiver Who Got Everything",
  "genre": "inheritance_dispute",
  "hook": "My aunt changed her will four months after her caregiver started. The caregiver got the house. We got nothing.",
  "card_text": '"Patricia needs her rest. Call ahead next time." That\'s what Sandra told me when I showed up on a Sunday. So I hired an elder law attorney instead. The court reinstated the original will.',
  "narration": (
    '"Patricia needs her rest. Call ahead next time." Sandra said that to me from the doorway of my aunt\'s house on a Sunday afternoon in September, '
    "nine months before Patricia died. I had driven two hours without warning because Patricia had not answered my calls in eleven days.\n\n"
    "I took note of the phrasing. Then I drove home.\n\n"
    "Patricia had no children. She was the family anchor — sharp, fiercely independent, deeply attached to the six of us who visited on rotation. "
    "Sandra had been hired as her in-home aide eight months earlier, after Patricia's hip replacement. "
    "From the beginning something had felt systematically wrong. Sandra was present at every family visit. "
    "She answered questions before Patricia could. She referred to Patricia's possessions as ours. "
    "When I mentioned this to my cousins they told me I was overreacting.\n\n"
    "Patricia died in January. The will was read in February. "
    "Sandra received the house — appraised at three hundred and forty thousand dollars — plus ninety thousand in savings. "
    "All six of us received nothing. The will had been rewritten the previous October, four months after Sandra was hired, "
    "with Sandra accompanying Patricia to the attorney's office and waiting in the room.\n\n"
    "I retained an elder law attorney the same week the will was read.\n\n"
    "We requested Patricia's medical records. In October, when the will was signed, her physician had formally documented moderate cognitive decline — "
    "a diagnosis that required additional safeguards before she could legally execute a new will. "
    "No safeguards had been observed. The attorney had recorded no independent capacity assessment. "
    "Sandra had driven Patricia to the appointment.\n\n"
    "We contested the will on grounds of undue influence and incapacity. Sandra's attorney fought it for seven months. "
    "The court found in our favor and reinstated the original will. Patricia's estate was distributed to the family as she had intended before Sandra arrived.\n\n"
    "Investigators also found that Sandra had made twelve withdrawals from Patricia's personal account during her months of employment, "
    "totaling fourteen thousand dollars. She was charged with financial exploitation of a vulnerable adult.\n\n"
    "Sandra called me once after the verdict. I let her leave a message. I did not return it.\n\n"
    "The house was sold. My share covered my daughter's first year of college.\n\n"
    "I still drive up on the Sundays I used to visit Patricia. "
    "I stop at the cemetery and bring the same flowers she kept on her kitchen table.\n\n"
    "She was sharper than anyone gave her credit for, right up until she wasn't. "
    "What Sandra missed was that we had been paying attention the entire time.\n\n"
    "The call-ahead rule turned out to be the first thing that really mattered."
  ),
  "broll_keywords": ["elderly hands", "legal documents", "courthouse exterior", "family home", "cemetery flowers"],
  "hashtags": ["shorts", "storytime", "elderabuse", "inheritance", "justice", "drama"],
  "description": "Her caregiver told me to call ahead before visiting. I started paying closer attention instead. The court reinstated the original will.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_005": {
  "id": "story_005",
  "title": "The Charity That Didn't Exist",
  "genre": "inheritance_fraud",
  "hook": "My uncle left his estate to a foundation that turned out to have no IRS filing, no board, and one officer: the attorney who drafted the will.",
  "card_text": '"Leonard was clear. The estate has been handled." That\'s what Gary told us at the reading. So we asked to see the foundation\'s IRS filings. There were none. Gary pled guilty.',
  "narration": (
    '"Leonard was clear. The estate has been handled." Gary said that to my cousin and me across the conference table at the reading, '
    "with the kind of practiced calm that is meant to end conversations. "
    "My uncle had passed six weeks earlier. His estate — a paid-off house, investment accounts, and a collection of first-edition books — "
    "was valued at just over four hundred thousand dollars. "
    "According to the will Gary had drafted, everything was to go to the Leonard Hartwell Charitable Foundation for Community Arts.\n\n"
    "I asked for the foundation's EIN. Gary said he would follow up.\n\n"
    "He did not follow up. I looked it up myself.\n\n"
    "There was no IRS filing for the Leonard Hartwell Charitable Foundation for Community Arts. "
    "No Form 990. No 501(c)(3) determination letter. No registration with the state attorney general's charitable trust division, "
    "which is required for any organization soliciting funds or receiving bequests in the state.\n\n"
    "The foundation had been incorporated as an LLC eleven months before my uncle's will was revised. "
    "The sole registered officer was Gary.\n\n"
    "We retained a probate litigator the same week.\n\n"
    "The state bar opened an investigation when our attorney filed a complaint. "
    "The district attorney's office was separately contacted and began their own review. "
    "My uncle's medical records showed that at the time the revised will was signed, he had been recently hospitalized for a cardiac event "
    "and had been under sedation the previous week. No independent witness was present at the signing.\n\n"
    "Gary's practice had handled the estate planning of eleven elderly clients over four years. "
    "Investigators eventually identified three other cases with similar structures — charitable bequests to entities Gary controlled "
    "that had never conducted any charitable activity.\n\n"
    "The will was contested. The court invalidated the bequest. "
    "My uncle's estate was distributed according to his previous will, which divided it equally between my cousin, my aunt, and two family friends he had named years before.\n\n"
    "Gary surrendered his law license and pled guilty to three counts of fraud. "
    "He was sentenced to four years and ordered to pay full restitution across all cases.\n\n"
    "The first-edition books went to my cousin, who keeps them in a glass case in her living room. "
    "My uncle had spent forty years collecting them. She dusts them on Sundays.\n\n"
    "My uncle trusted Gary for over a decade. Gary mistook that trust for a window.\n\n"
    "The EIN lookup took about four minutes."
  ),
  "broll_keywords": ["legal documents", "courthouse exterior", "old books", "lawyer office", "family home"],
  "hashtags": ["shorts", "storytime", "inheritance", "fraud", "justice", "drama"],
  "description": "The foundation that inherited everything had no IRS filing, no board, and one officer — the attorney who drafted the will.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_008": {
  "id": "story_008",
  "title": "What Grandpa Hid In The Bible",
  "genre": "family_inheritance",
  "hook": "My uncle threatened to walk out of my grandfather's life if the will wasn't changed in his favor. My grandfather changed it. Just not the way Robert expected.",
  "card_text": '"Change the will or I walk. Die alone for all I care." That\'s what my uncle Robert told my grandfather. So Grandpa wrote a codicil by hand and hid it in his Bible. Robert never saw it coming.',
  "narration": (
    '"Change the will or I walk. Die alone for all I care." My uncle Robert said that to my grandfather in the kitchen of the house where my grandfather had lived for fifty-one years. '
    "Robert wanted the property reclassified as his primary residence for tax purposes. "
    "My grandfather had refused. Robert made his position clear and left without finishing his coffee.\n\n"
    "My grandfather did not call us to talk about it. He went to his desk.\n\n"
    "My grandfather was eighty-four and had been a county clerk for thirty-two years before he retired. "
    "He understood legal documents the way some people understand weather — by instinct and long observation. "
    "He knew that a handwritten will or codicil, if signed and dated and witnessed, is valid in our state without an attorney. "
    "He had known this for decades.\n\n"
    "He wrote a codicil by hand on the back of a piece of graph paper. "
    "He had his neighbor Edna and her husband Gerald witness and sign it the same afternoon. "
    "Then he folded it in quarters and tucked it inside the family Bible, behind the page where his own birth had been recorded in his mother's handwriting in 1939.\n\n"
    "He passed fourteen months later. Robert arrived at the funeral in a rental car and spoke at length about reconciliation.\n\n"
    "The estate attorney read the original will first. It was what Robert expected — a three-way split between Robert, my father, and my aunt. "
    "Then she read the codicil.\n\n"
    "The codicil amended the distribution to remove Robert entirely. "
    "His share was redistributed equally between my father and my aunt. "
    "The codicil also specified that if Robert contested the amendment, his portion would instead go to the county library's archive fund.\n\n"
    "Robert's attorney sent a letter within three weeks suggesting the codicil was invalid. "
    "He cited my grandfather's age and alleged incapacity. "
    "Edna and Gerald were both present and willing to testify. "
    "My grandfather's physician confirmed that at the time the codicil was written, he had attended a regular checkup and been assessed as cognitively intact.\n\n"
    "Robert did not file a formal contest.\n\n"
    "My father and aunt settled the estate without incident. "
    "The house was sold. My aunt used her share to pay off her mortgage. "
    "My father put his in a college account for my youngest sister.\n\n"
    "The Bible sits on a shelf in my father's study now. "
    "He has never moved the codicil from where my grandfather left it.\n\n"
    "Robert sent a card at Christmas for two years afterward. "
    "No one responded.\n\n"
    "My grandfather spent thirty-two years watching people argue over documents. "
    "He knew exactly what he was doing when he folded that piece of graph paper and put it behind his own name."
  ),
  "broll_keywords": ["old bible", "legal documents", "family home", "courthouse exterior", "elderly hands"],
  "hashtags": ["shorts", "storytime", "familydrama", "inheritance", "justice", "drama"],
  "description": "My uncle threatened to walk out of my grandfather's life if the will wasn't changed. My grandfather changed it. Just not in Robert's favor.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_009": {
  "id": "story_009",
  "title": "The Toast That Ended Everything",
  "genre": "friendship_betrayal",
  "hook": "My best friend gave a toast at my wedding and used it to confess his feelings for my husband. In front of two hundred people.",
  "card_text": '"Marcus, I\'ve always been in love with you. I just wanted you to know." That\'s what Jess said into a microphone at my wedding reception. So I set down my champagne glass. What came next, he didn\'t expect.',
  "narration": (
    '"Marcus, I\'ve always been in love with you. I just wanted you to know." '
    "Jess said that into a microphone at my wedding reception, in front of two hundred people, including both our families, "
    "my new in-laws, and my grandmother, who was visiting from out of state for the first time in four years.\n\n"
    "I set my champagne glass on the table.\n\n"
    "Jess and I had been friends since the second year of college. I had been the person who helped him through two breakups, "
    "a job loss, and the death of his father. I had asked him to give a toast because I trusted him. "
    "Marcus and I had been together for six years. Jess had known the entire time.\n\n"
    "The room went quiet after Jess finished speaking. Then it did not go quiet in the way a room goes quiet when someone says something beautiful. "
    "Marcus looked at me. I looked at Marcus. I picked up my glass and drank what was in it and set it back down without expression.\n\n"
    "I did not respond to Jess from the dais. I did not approach him during cocktail hour. "
    "I danced with my husband, thanked our guests, and cut the cake. "
    "We left on schedule.\n\n"
    "In the car I told Marcus that I would handle it and that it would not touch us unless we let it. "
    "He said okay. That was the last time we discussed Jess for about three weeks.\n\n"
    "When we returned from our honeymoon I wrote Jess a card. Three sentences. "
    "The first acknowledged what he had said. The second said that I understood he must be carrying something very heavy to have made that choice. "
    "The third said that I wished him well and that what we had was finished.\n\n"
    "I left it in his mailbox. I did not ring the bell.\n\n"
    "He called four times over the following month. I did not answer. "
    "He sent a long message explaining that he had meant it as a tribute to how much Marcus meant to him, not a disruption. "
    "I read it twice, put the phone face-down, and went back to what I had been doing.\n\n"
    "Mutual friends reached out over the following year asking if I had heard from Jess, whether things might be repaired. "
    "I told them I wished him well and left it there.\n\n"
    "Marcus and I will have been married four years in June. We have a house with a yard and a dog named after a street we walked on our first trip to Portugal. "
    "We host dinners on Saturdays. Our friends come and bring wine and stay late.\n\n"
    "Jess was not wrong that he was carrying something heavy. "
    "What he was wrong about was thinking my wedding reception was the place to put it down.\n\n"
    "The card is in the recycling. The marriage is not."
  ),
  "broll_keywords": ["wedding reception", "champagne glasses", "city streets", "couple walking", "dinner party"],
  "hashtags": ["shorts", "storytime", "betrayal", "wedding", "drama", "relationships"],
  "description": "My best friend used his toast at my wedding to confess his feelings for my husband. I set down my champagne glass and handled it quietly.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_012": {
  "id": "story_012",
  "title": "The HOA President and the Wrong Color",
  "genre": "hoa_drama",
  "hook": "The HOA president fined me for painting my shutters a color she claimed violated the guidelines. The guidelines didn't exist yet when I painted them.",
  "card_text": '"The color has been removed from the approved list. The fine stands." That\'s what Margaret told me at the board meeting. So I requested every dated document in the HOA\'s records. The board voted four to one to remove her.',
  "narration": (
    '"The color has been removed from the approved list. The fine stands." '
    "Margaret said that to me at the October board meeting, from the head of the folding table, "
    "with the particular patience of someone who has never been questioned before.\n\n"
    "I opened my folder.\n\n"
    "I had painted my shutters the previous April — a deep slate blue called Coastal Fog, chosen from the approved color palette "
    "that was published on the HOA website at the time. I had saved a screenshot with the date stamp. "
    "Three weeks after the work was completed, I received a notice of violation and a two-hundred-and-fifty-dollar fine. "
    "The notice cited a color restriction that had not been in place when I painted.\n\n"
    "I submitted a records request to the HOA management company for all board meeting minutes, approved color palette revisions, "
    "and any documentation showing when Coastal Fog had been removed from the approved list. "
    "State law required a response within thirty days.\n\n"
    "The records arrived on day twenty-eight. I went through them on a Saturday afternoon with a yellow legal pad.\n\n"
    "The color revision list that Margaret had cited was dated six weeks after my paint job. "
    "The minutes from the meeting where the revision was allegedly approved showed a quorum of three board members. "
    "The HOA bylaws required a quorum of four for any amendment to the community standards. "
    "The vote had not been valid.\n\n"
    "I also found that Margaret had issued fourteen fines in the previous eighteen months using the same color list — "
    "all of them after the invalid vote, all of them citing colors that had been on the approved palette at the time of installation.\n\n"
    "I brought the documentation to the November board meeting and presented it in order. "
    "I spoke for nine minutes. I did not raise my voice.\n\n"
    "The board voted four to one to rescind all fourteen fines and to formally invalidate the October revision to the color standards. "
    "They also voted four to one to open a review of Margaret's conduct as president.\n\n"
    "Margaret voted against both motions. She was the one.\n\n"
    "She resigned the following January, citing personal reasons. "
    "The new board president sent a letter to the neighborhood in February acknowledging the errors and confirming that no homeowner owed any outstanding balance from the disputed fines.\n\n"
    "I got my two hundred and fifty dollars back.\n\n"
    "My shutters are still Coastal Fog. "
    "They look exactly as they did the day the painter finished — which is to say, they look fine.\n\n"
    "The new president waves to me when she walks her dog past the house. "
    "We have not discussed Margaret. There is nothing left to discuss."
  ),
  "broll_keywords": ["suburban house", "painted shutters", "neighborhood street", "legal documents", "community meeting"],
  "hashtags": ["shorts", "storytime", "HOAdrama", "justice", "neighbors", "drama"],
  "description": "She fined me for a color that wasn't restricted when I painted. I requested all the records and found fourteen invalid fines. The board removed her.",
  "estimated_duration": 160,
  "target_duration": 160,
},

"story_013": {
  "id": "story_013",
  "title": "He Rewrote The Will In The Hospital Room",
  "genre": "inheritance_manipulation",
  "hook": "My grandmother's will was rewritten while she was on morphine. The new version left everything to the cousin who arranged the signing.",
  "card_text": '"She wanted this done while she still could. I was just helping her." That\'s what Victor said when we confronted him. So we requested the morphine administration log from the hospital. The court invalidated the will and Victor paid our costs.',
  "narration": (
    '"She wanted this done while she still could. I was just helping her." '
    "Victor said that to my father and me in the hospital corridor on the second day after my grandmother's surgery, "
    "standing between us and her room with his arms crossed.\n\n"
    "I asked to see the document. He said it had already been filed with her attorney.\n\n"
    "My grandmother Cecelia had been hospitalized for a fractured hip. She was eighty-seven. "
    "The surgery had gone well but the recovery required significant pain management. "
    "Victor, her youngest grandson and the family's self-appointed coordinator, had arrived from out of state the morning after she was admitted. "
    "He had been there for a total of four hours when the revised will was signed.\n\n"
    "We retained a probate attorney within the week.\n\n"
    "She requested the hospital's medication administration records for the twenty-four hours surrounding the signing. "
    "My grandmother had received IV morphine at a dose consistent with post-surgical pain management — "
    "four administrations in the nine hours before the document was executed. "
    "Her attending physician had not been consulted about her capacity to sign legal documents. "
    "The notary Victor had arranged was a mobile notary he had found online the morning of the visit.\n\n"
    "The revised will left the entirety of my grandmother's estate — her house, her savings, and a small portfolio her husband had built over forty years — "
    "to Victor. The previous will, in place for over a decade, had divided everything equally among her four grandchildren.\n\n"
    "The will was contested on grounds of incapacity and undue influence. "
    "Victor hired an attorney and argued that our grandmother had been alert and lucid. "
    "His attorney did not subpoena the medication records.\n\n"
    "We did.\n\n"
    "The court found that adequate capacity could not be established given the documented medication levels and the absence of any independent assessment. "
    "The revised will was invalidated. Victor was ordered to pay a portion of our legal costs.\n\n"
    "My grandmother recovered and went home to her house, which remained hers. "
    "She knew a contest had been filed but we did not discuss the details with her. "
    "She had enough to carry.\n\n"
    "Victor did not attend the next two family gatherings. When he finally appeared, he said nothing about the case and neither did we.\n\n"
    "My grandmother passed two years later, in her own bed, in the house she had lived in for forty-four years. "
    "The original will was executed without dispute.\n\n"
    "She had asked to be buried with her husband's watch. We made sure of it.\n\n"
    "Victor sent flowers to the service. We acknowledged them and moved on."
  ),
  "broll_keywords": ["hospital hallway", "elderly hands", "legal documents", "courthouse exterior", "family home"],
  "hashtags": ["shorts", "storytime", "inheritance", "familydrama", "justice", "drama"],
  "description": "The will was rewritten while she was on morphine. We requested the medication log. The court invalidated it and ordered him to pay our costs.",
  "estimated_duration": 160,
  "target_duration": 160,
},

}  # end REWRITES


# ─────────────────────────────────────────────────────────────────────────────
# 15 NEW STORIES  (appended after existing list)
# ─────────────────────────────────────────────────────────────────────────────
NEW_STORIES = [

{
  "id": "story_057",
  "title": "The Patent He Didn't Know I Had",
  "genre": "workplace_reversal",
  "hook": "My boss fired me for poor performance. Six months later his company's lead product ran directly on a patent I owned.",
  "card_text": '"You\'ve always needed supervision. This position requires independence." That\'s what my boss said when he let me go. So I went home and called my patent attorney. The settlement was eight hundred and forty thousand dollars.',
  "narration": (
    '"You\'ve always needed supervision. This position requires independence." '
    "Dennis said that to me in the HR conference room on a Wednesday morning in March, "
    "with a severance packet already printed and waiting on the table.\n\n"
    "I signed the paperwork, collected my laptop bag, and went home.\n\n"
    "I had been a senior engineer at the company for six years. For three of those years I had been working on a compression protocol "
    "for handling large-scale data transfers across distributed networks. "
    "The work had begun before I joined the company — I had developed the initial architecture on my own time, "
    "on my own equipment, before I was ever hired. "
    "I had filed for the patent eighteen months before my first day at the office.\n\n"
    "When I joined the company I had disclosed the patent in my onboarding paperwork. "
    "HR had logged it and no one had followed up.\n\n"
    "Dennis had hired me in part to build out infrastructure that used similar compression principles. "
    "What Dennis did not know — because he had not read the onboarding file — was that the production architecture "
    "his team had shipped in Q3 was built on top of my protocol. Not similar to it. On top of it.\n\n"
    "I called my patent attorney the afternoon I was let go.\n\n"
    "She filed a demand letter within three weeks. The company's legal team responded six days later requesting a meeting. "
    "The meeting lasted four hours. Their engineers confirmed the implementation. "
    "Their IP counsel confirmed the filing date. "
    "The prior disclosure in my onboarding paperwork confirmed I had not assigned the rights to anyone.\n\n"
    "The settlement was eight hundred and forty thousand dollars plus a licensing agreement for continued use.\n\n"
    "Dennis was let go three months after the settlement. The VP of engineering who had overseen the architecture decision "
    "took a leave of absence. I was not involved in either outcome.\n\n"
    "I consulted for two years and then started my own practice. "
    "The licensing royalties come in quarterly. I have not needed the severance money.\n\n"
    "I think about that conference room sometimes. The printed paperwork. "
    "The particular confidence of someone who has never been wrong in a way that cost him anything.\n\n"
    "Dennis was right that the position required independence. "
    "He was wrong about who had it."
  ),
  "broll_keywords": ["office building", "legal documents", "laptop computer", "city skyline", "coffee shop"],
  "hashtags": ["shorts", "storytime", "workplace", "justice", "revenge", "drama"],
  "description": "My boss fired me for lacking independence. He didn't know I held the patent his flagship product was built on.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_058",
  "title": "The Signature She Needed",
  "genre": "workplace_reversal",
  "hook": "A senior partner told me I didn't have the temperament for partnership. Ten years later I was the one who had to sign off on his biggest deal.",
  "card_text": '"You don\'t have the temperament for partnership. It\'s a difficult truth but you deserve to hear it." That\'s what Richard told me before I left the firm. So I built my own practice. Years later he needed my signature to close.',
  "narration": (
    '"You don\'t have the temperament for partnership. It\'s a difficult truth but you deserve to hear it." '
    "Richard said that to me in his office at the end of my fifth year at the firm, "
    "with the door closed and his reading glasses folded on the desk in front of him, "
    "the way he arranged things when he wanted the conversation to feel considered.\n\n"
    "I thanked him for his time and took the elevator down.\n\n"
    "I had been a corporate associate for five years. "
    "My billing numbers were strong. My client feedback had been consistently positive. "
    "What I had lacked, according to Richard, was the willingness to absorb ambiguity without visible distress. "
    "What I understood him to mean was that I raised questions he found inconvenient.\n\n"
    "I joined a smaller firm for eighteen months, then went in-house as general counsel at a mid-sized technology company. "
    "The company was acquired three years in. After the acquisition I built a boutique practice advising on complex transactions — "
    "the kind that require someone with corporate, regulatory, and operational experience across the table.\n\n"
    "Richard's firm had grown significantly in the intervening decade. "
    "They were representing the target in a major acquisition — the largest deal in their practice group's history, "
    "by their own account in the trade press.\n\n"
    "I was representing the acquirer.\n\n"
    "I recognized Richard's name on the signature block of the opposing representation letter. "
    "I did not mention the history to my client. I ran the process the way I run every process — "
    "methodically, with full documentation, and without urgency that wasn't warranted.\n\n"
    "We closed in eight months. "
    "Richard and I sat across the closing table twice. "
    "He acknowledged me both times with professional courtesy. "
    "I returned it in kind.\n\n"
    "At the final signing session, his associate leaned over and mentioned that Richard spoke highly of me to the client. "
    "I said I was glad the process had gone smoothly.\n\n"
    "I do not know if Richard remembered what he said in that office. "
    "It does not affect my work either way.\n\n"
    "My practice is fully retained through next year. "
    "I am selective about which transactions I take on. "
    "I raise questions when questions are warranted.\n\n"
    "That part has not changed."
  ),
  "broll_keywords": ["lawyer office", "conference room", "city skyline", "legal documents", "handshake"],
  "hashtags": ["shorts", "storytime", "workplace", "career", "justice", "drama"],
  "description": "A senior partner said I lacked the temperament for partnership. A decade later he needed my signature to close his biggest deal.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_059",
  "title": "Forty Percent Followed Me Out",
  "genre": "workplace_reversal",
  "hook": "My VP killed my project and restructured my team away. Eighteen months later forty percent of the company's revenue walked out the door with me.",
  "card_text": '"We\'re going in a different direction. Your role doesn\'t fit where we\'re headed." That\'s what my VP said in the restructuring meeting. So I left. My largest client called me the following Monday.',
  "narration": (
    '"We\'re going in a different direction. Your role doesn\'t fit where we\'re headed." '
    "Paul said that to me at 4pm on a Thursday in November, with the org chart on the screen behind him "
    "already redrawn without my name on it.\n\n"
    "I asked about the timeline. He said end of month. I said I understood, and I left his office.\n\n"
    "I had been at the company for seven years and had built the client services division from three accounts to nineteen. "
    "Our largest client — a national healthcare organization that represented roughly forty percent of division revenue — "
    "had renewed their contract twice specifically citing my team's work.\n\n"
    "Paul had recently been brought in to \"operationalize\" the division, which in practice meant reducing headcount "
    "and consolidating my function into a lower-cost model under a director who had been at the company for eight months.\n\n"
    "I spent the last two weeks of the month documenting my handoff materials carefully. "
    "I turned in my equipment on the last day of the month and left without a departure announcement.\n\n"
    "I spent the first week at home reading. The second week I called a few former colleagues. "
    "On the Monday of my third week, my phone rang. "
    "It was the senior VP at the healthcare organization. "
    "She said she had heard I was no longer with the company. She said their renewal was coming up in ninety days. "
    "She asked whether I had plans.\n\n"
    "I told her I was available.\n\n"
    "We signed an engagement letter the following week. "
    "Over the next six months, three other former clients reached out through similar channels. "
    "By the end of my first year in business I had more revenue than I had managed in my last full year at the company, "
    "and a lower cost structure.\n\n"
    "Paul's restructured division missed its targets for two consecutive quarters. "
    "I read about it in a trade newsletter that still had my old email address.\n\n"
    "The healthcare client has been with me for three years now. "
    "They have referred two additional clients. We work well together.\n\n"
    "I think the part Paul misunderstood is that client relationships are not attached to org charts. "
    "They are attached to people.\n\n"
    "He was right that my role didn't fit where they were headed. "
    "He was wrong about where that left me."
  ),
  "broll_keywords": ["office building", "city skyline", "business meeting", "laptop computer", "coffee shop"],
  "hashtags": ["shorts", "storytime", "workplace", "career", "justice", "drama"],
  "description": "My VP restructured my role away. Forty percent of company revenue followed me out the door eighteen months later.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_060",
  "title": "The Key In The Tackle Box",
  "genre": "inheritance_manipulation",
  "hook": "My stepbrother used our father's dementia to change the will. My father had left a second key behind where only I knew to look.",
  "card_text": '"Dad made his intentions very clear. This is what he wanted." That\'s what my stepbrother said at the reading. So I drove to my father\'s fishing cabin. The key was exactly where he told me it would be.',
  "narration": (
    '"Dad made his intentions very clear. This is what he wanted." '
    "Derek said that at the reading, with his attorney beside him and the revised will on the table, "
    "his posture the practiced ease of someone who had been rehearsing the moment.\n\n"
    "I said nothing. I drove to my father's fishing cabin that afternoon.\n\n"
    "My father had been diagnosed with early-stage vascular dementia two years before he passed. "
    "In the first year after the diagnosis, before his condition progressed significantly, he had told me something. "
    "We had been sitting on the dock at the cabin, the way we had been doing since I was a boy. "
    "He told me he was worried about Derek. He told me he had put something important in a safety deposit box at the small credit union "
    "in the county where the cabin was — not the bank he used in the city, where Derek had been added as an authorized signer. "
    "He told me the key was in his old tackle box, in the front mesh pocket, underneath the leader line.\n\n"
    "He made me repeat it back to him. I did.\n\n"
    "The cabin was unlocked. The tackle box was on the shelf where it had always been. "
    "The key was in the front mesh pocket.\n\n"
    "I drove to the credit union the next morning when they opened. "
    "My father had listed me as the co-holder on the box. The woman at the counter confirmed it from the card on file.\n\n"
    "Inside the box was a handwritten letter, signed and dated, describing his concerns about Derek's influence over his affairs, "
    "documenting two specific instances where Derek had attempted to redirect account access without authorization, "
    "and expressing his clear intention that the original will — the one Derek had gotten revised — reflected coercion, not his wishes.\n\n"
    "There was also a copy of the original will and a notarized affidavit my father had signed with a different attorney, "
    "one Derek did not know about, six weeks before his condition deteriorated significantly.\n\n"
    "We filed a contest within the month. Derek's attorney withdrew after reviewing the affidavit. "
    "The court reinstated the original distribution.\n\n"
    "My father had been two steps ahead even as his memory slipped. "
    "He trusted that I would go to the cabin. He trusted that I would remember.\n\n"
    "I did."
  ),
  "broll_keywords": ["fishing lake", "tackle box", "bank vault", "legal documents", "family cabin"],
  "hashtags": ["shorts", "storytime", "inheritance", "familydrama", "justice", "drama"],
  "description": "My stepbrother used my father's dementia to change the will. Dad had left a key in his tackle box and I knew exactly where to look.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_061",
  "title": "The CPA in the Family",
  "genre": "estate_fraud",
  "hook": "My sister was named executor of our mother's estate. When I asked for a formal accounting, she said the estate was too complex to explain.",
  "card_text": '"The estate is complex. I\'m protecting all of us." That\'s what my sister said when I asked for receipts. So I requested a formal accounting through the probate court. I found sixty-seven thousand in unauthorized fees.',
  "narration": (
    '"The estate is complex. I\'m protecting all of us." '
    "Renata said that to me on the phone in a tone that made it clear she expected the subject to close.\n\n"
    "I waited three days and then filed a request for a formal accounting through the probate court.\n\n"
    "I had retired from public accounting after thirty-one years. "
    "I had spent the last eighteen of those years in forensic accounting, reviewing estates, trusts, and financial records in disputed cases. "
    "Renata knew this. She had been the one who called me every year to help with her personal taxes.\n\n"
    "Our mother had passed with an estate worth just over four hundred thousand dollars: a house, two investment accounts, and a savings balance. "
    "The will divided everything equally between Renata and me. "
    "Renata had been named executor.\n\n"
    "Fourteen months after probate opened, I had received no formal accounting, two delayed responses to written inquiries, "
    "and a single phone call in which Renata described vague complexities without documentation.\n\n"
    "The court-ordered accounting arrived six weeks after my filing.\n\n"
    "I went through it on a Friday afternoon. "
    "There were sixty-seven thousand dollars in management and administrative fees billed against the estate over fourteen months. "
    "No fee agreement had been executed at the time of appointment. "
    "The hourly rate applied was nearly three times the prevailing rate for estate administration in our county. "
    "Several of the billed hours corresponded to dates when probate court records showed no activity.\n\n"
    "I prepared a written analysis and submitted it to the probate court and the state bar's executor oversight division.\n\n"
    "The court found Renata had breached her fiduciary duty. "
    "She was removed as executor, ordered to return sixty-one thousand dollars to the estate, "
    "and required to pay my legal costs from her own portion of the distribution.\n\n"
    "The estate closed four months later. I received my share in full.\n\n"
    "Renata and I have not spoken since the hearing. "
    "She sent one message saying she thought I had overreacted. I did not reply.\n\n"
    "Thirty-one years of accounting taught me many things. "
    "The most important is that complexity is rarely the explanation. "
    "It is usually the alibi."
  ),
  "broll_keywords": ["spreadsheet on computer", "legal documents", "courthouse exterior", "elderly hands", "family home"],
  "hashtags": ["shorts", "storytime", "inheritance", "familydrama", "justice", "drama"],
  "description": "My sister said the estate was too complex to explain. I was a retired forensic accountant. I found sixty-seven thousand in unauthorized fees.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_062",
  "title": "The Copy the Attorney Kept",
  "genre": "inheritance_fraud",
  "hook": "My nephew changed our grandmother's will and fired the family attorney who'd handled her affairs for twenty years. The attorney kept a signed copy.",
  "card_text": '"Grandma finally saw things clearly. The attorney she had was out of touch with what she needed." That\'s what my nephew told us. So we called the original attorney. She had kept a signed copy in her personal files.',
  "narration": (
    '"Grandma finally saw things clearly. The attorney she had was out of touch with what she needed." '
    "Tyler said that at Thanksgiving, with the practiced sincerity of someone who had been framing the story for months.\n\n"
    "No one responded. We passed the rolls.\n\n"
    "Our grandmother Miriam had used the same estate attorney — a woman named Patricia — for twenty-three years. "
    "Patricia had drafted the original will, the amendments, the trust documents, the healthcare directives. "
    "She knew the family's history in the way that only a long-term advisor does.\n\n"
    "Four months before my grandmother died, Tyler had called Patricia's office and terminated the representation on Miriam's behalf. "
    "He then brought in a different attorney and revised the will. "
    "The revised will left the entirety of the estate — the house, the accounts, the family jewelry collection — to Tyler. "
    "The three of us received nothing.\n\n"
    "When my grandmother passed, I called Patricia the following morning.\n\n"
    "She had expected the call. She had not been comfortable with how the termination had been handled. "
    "She told me she had retained a copy of the most recent will she had prepared for Miriam — "
    "a comprehensive document with specific, reasoned distributions — signed, witnessed, and executed fourteen months before the revision. "
    "She had kept it in her personal files, not the client file, because the client file had been transferred to Tyler's attorney.\n\n"
    "She was willing to testify.\n\n"
    "We retained a probate litigator. "
    "Medical records showed that in the months before the revision, my grandmother had been prescribed new medications "
    "with documented cognitive side effects. Tyler had been her only visitor during that period.\n\n"
    "The will was contested. Tyler's attorney withdrew before the hearing. "
    "The court invalidated the revised will. Patricia's document was admitted and the estate was distributed according to its terms.\n\n"
    "Tyler did not attend the following Thanksgiving. "
    "No one brought up his name and no one needed to.\n\n"
    "Patricia retired the following year. I sent her a card. "
    "She had spent twenty-three years doing her job carefully and honestly, and when it mattered most she had kept the document.\n\n"
    "Sometimes the person who protects you is the one you never thought to thank."
  ),
  "broll_keywords": ["lawyer office", "legal documents", "elderly hands", "courthouse exterior", "family gathering"],
  "hashtags": ["shorts", "storytime", "inheritance", "familydrama", "justice", "drama"],
  "description": "My nephew fired our grandmother's longtime attorney before changing the will. The attorney had kept a signed copy in her personal files.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_063",
  "title": "The Head For Business",
  "genre": "family_rejection",
  "hook": "My father said at Thanksgiving that my brother had the head for business and I never did. I spent the next twelve years proving him wrong.",
  "card_text": '"Your brother has the head for business. You never did, and that\'s all right." That\'s what my father said at the Thanksgiving table when I was twenty-six. So I went home and got to work. He sat across my desk fourteen years later.',
  "narration": (
    '"Your brother has the head for business. You never did, and that\'s all right." '
    "My father said that at the Thanksgiving table when I was twenty-six. "
    "My brother Wayne had just announced he was joining the family distribution company. "
    "I was working at a regional bank and had been quietly planning to leave.\n\n"
    "I thanked my father for the turkey and drove home that evening.\n\n"
    "I left the bank in January and took a position at a logistics startup that no one had heard of. "
    "I stayed for four years, learned how freight networks actually worked at the operational level, "
    "and left when the company was acquired to start my own practice advising mid-market distributors on network efficiency.\n\n"
    "The work was not glamorous. I drove to warehouses in industrial parks. "
    "I read shipping manifests and walked floor plans and asked the people who actually moved things what slowed them down.\n\n"
    "By year eight I had sixteen clients and a staff of nine. By year twelve I had sold a partial stake to a private equity firm "
    "for an amount that made the news in the trade press.\n\n"
    "My father's distribution company had not kept pace with the industry. "
    "Wayne had run it competently but without the structural changes it needed. "
    "They had lost two major contracts to competitors who had implemented the kind of network redesign I had been helping other companies do for a decade.\n\n"
    "My father called me and asked if we could meet. I invited him to my office.\n\n"
    "He sat in the chair across the desk — the same desk I had bought with my first year of profitability. "
    "My assistant brought coffee and called me by my title when she knocked.\n\n"
    "My father said the company needed a strategic review. He said Wayne agreed. "
    "He said he should have paid closer attention to what I was doing.\n\n"
    "I told him I would send over an engagement framework the following week.\n\n"
    "We worked together for two years. The company stabilized. I billed at my standard rate and did the work carefully.\n\n"
    "He never mentioned Thanksgiving. I never brought it up.\n\n"
    "Wayne and I are cordial. We see each other at holidays. "
    "He has never asked what my father said in my office that afternoon, and I have never told him.\n\n"
    "There was nothing to say. The work said it."
  ),
  "broll_keywords": ["modern office", "warehouse interior", "business meeting", "city skyline", "family dinner"],
  "hashtags": ["shorts", "storytime", "family", "career", "success", "drama"],
  "description": "My father said my brother had the head for business and I never did. He sat across my desk fourteen years later asking for help.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_064",
  "title": "Why Can't You Be More Like Your Sister",
  "genre": "family_rejection",
  "hook": "My mother spent years comparing me to my sister. When my sister's business failed, my mother called me for help and learned what I had quietly built.",
  "card_text": '"Why can\'t you be more like your sister? She takes initiative. She puts herself out there." My mother said that every year for a decade. So I kept working. When the calls finally came, I let the results speak.',
  "narration": (
    '"Why can\'t you be more like your sister? She takes initiative. She puts herself out there." '
    "My mother said versions of that to me for the better part of a decade — "
    "at graduation dinners, on Sunday calls, in the half-apologetic tone of someone who believes they are offering useful feedback.\n\n"
    "I thanked her and continued what I was doing.\n\n"
    "My sister Dana had launched a retail concept at thirty-two with significant fanfare — "
    "a flagship store, press coverage in the regional lifestyle magazines, a waitlist my mother mentioned every time we spoke. "
    "She had always been the one who moved visibly and announced her progress in advance.\n\n"
    "I had taken a different path. I worked in supply chain compliance at a mid-sized manufacturer. "
    "The work was technical and largely invisible from the outside — regulatory filings, vendor audits, process documentation. "
    "I was good at it. I had been promoted three times in six years. "
    "I had also been quietly consulting on the side for two years, building a client list in industries with complex compliance needs.\n\n"
    "Dana's concept ran into difficulties in the third year. "
    "Supply chain disruptions, lease terms that had not accounted for the margin compression that followed, "
    "and a scaling decision made too quickly. The flagship closed. The second location never opened.\n\n"
    "My mother called me four days after the closure. She said she was worried about Dana. "
    "She asked if I knew anyone who could help Dana think through what to do next.\n\n"
    "I told her I would think about it.\n\n"
    "What came out over the next few weeks, as my mother asked more questions, "
    "was the accounting of what I had actually been doing. "
    "The consulting practice. The retained clients. The offer I had recently declined from a firm that wanted to acquire my client list.\n\n"
    "My mother was quiet for a long time when I explained the last part.\n\n"
    "I helped Dana work through a restructuring plan over the following months. "
    "She stabilized and eventually launched something smaller and more sustainable. "
    "We are closer now than we were before any of it.\n\n"
    "My mother and I speak on Sundays. She does not make comparisons anymore. "
    "I have never brought up the ones she made before.\n\n"
    "I did not build what I built to correct her opinion. "
    "I built it because the work was worth doing.\n\n"
    "The opinion corrected itself."
  ),
  "broll_keywords": ["retail store", "office desk", "city street", "family gathering", "coffee shop"],
  "hashtags": ["shorts", "storytime", "family", "career", "success", "drama"],
  "description": "My mother spent years asking why I couldn't be more like my sister. When the calls came, she learned what I had quietly built.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_065",
  "title": "I've Understood for Twenty-Eight Years",
  "genre": "parent_abandonment",
  "hook": "My father left when I was nine and came back twenty-eight years later to explain himself. I let him finish.",
  "card_text": '"I had to live my life. You would have understood if you were older." That\'s what my father said when he came back. So I listened to everything he had to say. Then I told him exactly what I understood.',
  "narration": (
    '"I had to live my life. You would have understood if you were older." '
    "My father said that to me across a restaurant table on a Tuesday evening in October. "
    "He had contacted me through my office — he had found me through a professional directory — "
    "and asked if we could meet. I had waited three weeks before responding. Then I said yes.\n\n"
    "He looked older than I expected. He had practiced the speech. I could tell.\n\n"
    "I was nine when he left. My mother had raised my brother and me alone, working two jobs through most of our childhood. "
    "He had sent money intermittently for the first few years and then stopped. "
    "I had heard from him twice during my twenties — a birthday card and a brief call when his own mother died. "
    "Each time I had responded politely and asked no questions.\n\n"
    "He spoke for about forty minutes. He described the pressures he had been under, the relationship he had entered, "
    "the circumstances that had made staying feel impossible. He said he had thought about reaching out many times. "
    "He said he hoped I had turned out all right. He said it looked like I had.\n\n"
    "I waited until he was finished.\n\n"
    "I told him I had turned out fine. I told him my brother had as well. "
    "I told him my mother had worked harder than she should have had to and that she was doing well. "
    "I told him I did not carry resentment the way he might expect, because resentment requires ongoing investment and I had spent mine elsewhere.\n\n"
    "Then I said: I do understand. I've understood for twenty-eight years. "
    "You needed to leave. You needed to stay gone. Those were your decisions and you made them. "
    "I made mine too.\n\n"
    "He asked if we could have dinner again sometime.\n\n"
    "I told him I would be in touch.\n\n"
    "I paid for the meal and took a cab back to my office. "
    "I had a conference call at eight and I did not want to be late.\n\n"
    "He sent an email two weeks later. I read it on a Sunday and thought about it. "
    "Then I closed the laptop and went for a walk.\n\n"
    "I have not decided what I want from the acquaintance, if anything. "
    "I am in no hurry to decide.\n\n"
    "What I know is that I sat across from him for forty minutes without adjusting my posture once. "
    "Nine-year-old me would have had something to say about that. "
    "Thirty-seven-year-old me just went back to work."
  ),
  "broll_keywords": ["restaurant table", "city street at night", "office building", "park walking", "morning coffee"],
  "hashtags": ["shorts", "storytime", "family", "healing", "abandonment", "drama"],
  "description": "My father left when I was nine and came back twenty-eight years later to explain himself. I let him finish. Then I told him what I understood.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_066",
  "title": "The Emergency Contact Change",
  "genre": "elder_fraud",
  "hook": "My father's new aide made herself his emergency contact and redirected his direct deposit without telling anyone. She was arrested three months after I filed.",
  "card_text": '"Your father trusts me more than you right now. Maybe think about why that is." That\'s what the aide said when I called to check in. So I called Adult Protective Services. She was arrested three months later.',
  "narration": (
    '"Your father trusts me more than you right now. Maybe think about why that is." '
    "Beverly said that to me when I called my father's cell phone and she answered. "
    "I asked to speak with him. She said he was resting.\n\n"
    "I called his landline. No answer. I called the aide agency. They said his care schedule had been modified at his request.\n\n"
    "I drove over that afternoon.\n\n"
    "My father was eighty and had recovered from a stroke the previous year. "
    "His cognition had been assessed as intact but his mobility had declined and he needed daily assistance. "
    "Beverly had been assigned through the agency eight months earlier. "
    "She was present during every one of my visits and had been gradually inserting herself into my father's administrative affairs — "
    "answering his phone, managing his appointment calendar, picking up his prescriptions.\n\n"
    "When I arrived he seemed comfortable but tired. He said Beverly was very helpful. "
    "He did not mention that she had been changed to his emergency contact, which I discovered by asking to see his medical ID card.\n\n"
    "I asked my father if he had authorized that. He said he didn't remember but maybe he had.\n\n"
    "I went home and pulled his bank account — I was joint on the account and had online access. "
    "His Social Security direct deposit had been redirected to a new account three weeks earlier. "
    "The authorization form had been signed with a signature that did not match his.\n\n"
    "I filed a report with Adult Protective Services that evening. I also called the local police non-emergency line. "
    "The following morning I called the aide agency and requested Beverly's immediate removal from my father's case.\n\n"
    "APS began an investigation. The bank confirmed the signature discrepancy and reversed the redirect. "
    "The police obtained Beverly's financial records and found that she had been redirecting direct deposits for two other elderly clients using the same method.\n\n"
    "She was arrested three months after my initial report. "
    "She pled guilty to financial exploitation of vulnerable adults across three counts and was sentenced to twenty-two months.\n\n"
    "My father moved closer to me the following spring. "
    "He has a new aide who has been with him for two years. I have met her family.\n\n"
    "Beverly was right that my father trusted her. "
    "She was wrong about what that meant for her."
  ),
  "broll_keywords": ["hospital corridor", "elderly hands", "bank statement", "suburban home", "family visit"],
  "hashtags": ["shorts", "storytime", "elderabuse", "caregiver", "justice", "drama"],
  "description": "My father's aide made herself his emergency contact and redirected his Social Security deposit. She was arrested three months after I filed the report.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_067",
  "title": "Forty Years of Trust",
  "genre": "elder_fraud",
  "hook": "A family friend managed my mother's finances for three years. When I finally looked at the records, ninety-four thousand dollars was gone.",
  "card_text": '"I\'ve known your mother for forty years. I\'m not going to let anything happen to her." That\'s what Howard told me when she gave him access. So I ran a forensic review. He pled guilty.',
  "narration": (
    '"I\'ve known your mother for forty years. I\'m not going to let anything happen to her." '
    "Howard said that to me at my mother's kitchen table three years before I found out what he had done. "
    "He had offered to help manage her finances after my father died — bill payment, investment account monitoring, insurance renewals. "
    "My mother was seventy-nine and overwhelmed. Howard had been my parents' friend since before I was born. "
    "She gave him access to her accounts.\n\n"
    "I am a forensic accountant. I had been for twenty-six years. "
    "I trusted Howard because my mother did, and because I assumed that trust had been earned over four decades.\n\n"
    "What prompted the review was not suspicion. It was my mother mentioning, almost in passing, "
    "that she had transferred money to help Howard with a real estate matter the previous spring. "
    "She said it was a loan. She could not tell me the amount.\n\n"
    "I asked for three years of statements. She gave me the online login.\n\n"
    "I spent a Saturday going through the records.\n\n"
    "There were ninety-four thousand dollars in outflows over thirty-eight months that I could not reconcile to any legitimate expense. "
    "The transfers varied in size and frequency — designed, I recognized, to stay below the reporting threshold. "
    "Some were labeled as investment contributions. Some were labeled as tax payments. "
    "None of them matched any actual tax liability or investment account I could identify.\n\n"
    "I called Howard that evening. He said the records were complex and offered to explain everything in person.\n\n"
    "I filed a report with the state attorney general's office the following morning and engaged the police financial crimes unit.\n\n"
    "Howard pled guilty fourteen months later to two counts of financial exploitation of a vulnerable adult. "
    "He was ordered to pay full restitution and received three years of supervised probation. "
    "He was in his late sixties. His attorney cited his age. The judge cited my mother's.\n\n"
    "My mother does not manage her own finances now. I do, directly.\n\n"
    "She asked me once whether she had been foolish. I told her she had been loyal, which is different.\n\n"
    "Howard was the one who made the choice to use forty years of trust as cover."
  ),
  "broll_keywords": ["bank statement", "elderly hands", "spreadsheet on computer", "courthouse exterior", "kitchen table"],
  "hashtags": ["shorts", "storytime", "elderabuse", "fraud", "justice", "drama"],
  "description": "A family friend managed my mother's finances for three years. When I reviewed the records I found ninety-four thousand dollars gone.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_068",
  "title": "Twenty Minutes on Camera",
  "genre": "elder_fraud",
  "hook": "The home care agency was billing twenty hours a week. When I checked the cameras I had installed, aides were showing up for twenty minutes.",
  "card_text": '"If you\'d been more present you\'d already know your father is well cared for." That\'s what the agency director said when I raised concerns. So I installed cameras. They showed up for twenty minutes while billing for four hours.',
  "narration": (
    '"If you\'d been more present you\'d already know your father is well cared for." '
    "The agency director said that to me in a phone call in March, in the tone of someone delivering a verdict. "
    "I had called to ask about the billing discrepancy I had noticed on the monthly invoice. "
    "He said the hours were accurate and the documentation was in order.\n\n"
    "I said I would follow up. I drove to the hardware store on the way home.\n\n"
    "My father was eighty-three and had Parkinson's. He needed several hours of daily assistance — "
    "meal preparation, medication management, mobility support. "
    "The agency had been contracted for twenty hours per week at a rate that was already at the high end of the market.\n\n"
    "I installed three cameras over a weekend — front door, kitchen, and living room. "
    "My father knew they were there. The agency did not.\n\n"
    "I reviewed the first week's footage on the following Sunday.\n\n"
    "Of the five scheduled four-hour visits that week, none ran longer than thirty-five minutes. "
    "Two were under twenty minutes. The aides arrived, completed minimal tasks, and left. "
    "On one occasion my father had not been given his noon medication because the aide was already gone by eleven-forty.\n\n"
    "I documented six weeks of footage before taking action. "
    "I wanted the pattern, not an incident.\n\n"
    "I filed complaints with the state health department, the department of labor, and the licensing board for home health agencies, "
    "attaching timestamped footage for each week I had documented.\n\n"
    "The licensing board opened an investigation. The health department conducted an unannounced audit. "
    "Three other families came forward with similar billing concerns during the investigation period.\n\n"
    "The agency's license was suspended and later revoked. "
    "The director and two supervisors were referred for fraud charges. "
    "The director was convicted of Medicaid billing fraud — my father's insurance had been billed in addition to our direct payment.\n\n"
    "My father has a private aide now, hired directly. She has been with him for eighteen months.\n\n"
    "The director was right that I could have been more present. "
    "What he didn't account for was that cameras are always present."
  ),
  "broll_keywords": ["security camera", "elderly hands", "home interior", "hospital corridor", "legal documents"],
  "hashtags": ["shorts", "storytime", "elderabuse", "caregiver", "justice", "drama"],
  "description": "They billed twenty hours a week. I installed cameras. They were showing up for twenty minutes and leaving.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_069",
  "title": "Guards a Gate Somewhere",
  "genre": "status_reversal",
  "hook": "My girlfriend's father said she could do better than someone who guards a gate. He said this at a military function where I was being promoted.",
  "card_text": '"He guards a gate somewhere, doesn\'t he? She could do better." That\'s what her father said to a colleague at a function. So I said nothing. His business partner snapped to attention when he saw me at the ceremony.',
  "narration": (
    '"He guards a gate somewhere, doesn\'t he? She could do better." '
    "Gerald said that to a colleague at a reception in the spring, not knowing I was twenty feet away. "
    "I heard it clearly. I adjusted my cufflinks and went to find my glass.\n\n"
    "Elena and I had been together for two years. Her father was a developer who had built a reasonable regional business "
    "and had the particular confidence that comes from being the most successful person in most rooms he entered. "
    "He had never asked what I did specifically. He had gathered the general outline from Elena and decided it was not impressive.\n\n"
    "He was not wrong that I was in the military. He was missing some context.\n\n"
    "I was a Lieutenant Colonel. I had commanded a battalion overseas and was currently serving in a role "
    "that involved advising on logistics infrastructure for domestic operations. "
    "The role was not visible from the outside. Most of my work was not.\n\n"
    "The promotion ceremony was held four months after that reception. "
    "It was a formal military event. Full dress. The kind of function where the room understands exactly what rank means.\n\n"
    "Elena had invited her parents. I had not suggested it but I had not discouraged it either.\n\n"
    "Gerald arrived with his wife and spent the first hour near the entrance with a drink, working his way through the room. "
    "I watched him stop when he reached a man near the far wall — a retired general who now sat on the board of Gerald's largest real estate investor.\n\n"
    "I watched the general recognize me. I watched him cross the room.\n\n"
    "I watched Gerald's expression change as the general spoke. As the general gestured toward the ceremony room. "
    "As Gerald pieced together what was being explained to him.\n\n"
    "Gerald came to find me after the ceremony. He shook my hand. He said he hadn't realized.\n\n"
    "I told him it was good to see him. Elena was standing next to me.\n\n"
    "We had dinner as a family six weeks later. Gerald asked thoughtful questions. "
    "I answered them. We have managed a cordial relationship since then.\n\n"
    "I never brought up what he said at the spring reception. There was no need.\n\n"
    "He learned what he needed to know from a general who had served with me. "
    "That is a better education than I could have provided."
  ),
  "broll_keywords": ["military ceremony", "formal event", "city skyline", "reception hall", "dress uniform"],
  "hashtags": ["shorts", "storytime", "military", "respect", "statusreversal", "drama"],
  "description": "Her father said I just guarded a gate somewhere. He said it at a military function. His own business partner was there to explain what he'd missed.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_070",
  "title": "The Welcome Note",
  "genre": "status_reversal",
  "hook": "My uncle mocked my startup at a family reunion the year it failed. Seven years later he took a job at a company in my portfolio. I approved his onboarding.",
  "card_text": '"He tried that startup thing. Lost everyone\'s money. Now he does consulting." That\'s what my uncle said at the reunion in front of the whole family. So I kept working. Seven years later I sent him a welcome note.',
  "narration": (
    '"He tried that startup thing. Lost everyone\'s money. Now he does consulting." '
    "Uncle Frank said that at the Fourth of July reunion, by the grill, to a cousin I had not seen in two years. "
    "He said it with the easy confidence of someone summarizing a well-established fact. "
    "I was standing eight feet away, filling a plate.\n\n"
    "I finished filling my plate and found a seat under the oak tree.\n\n"
    "The startup had failed — that was true. We had raised early-stage capital from family and friends and the product had not scaled the way the model required. "
    "I had returned what I could, worked out repayment plans for the rest, and moved on. "
    "What Frank called \"losing everyone's money\" was a three-year process that cost me significantly in reputation and sleep.\n\n"
    "The consulting was real. I had built a modest practice advising founders on operational infrastructure. "
    "Over five years it had grown into something different — a small fund that took positions in early-stage companies "
    "and provided advisory support alongside capital. We had four portfolio companies. Three had grown substantially.\n\n"
    "The acquisition was announced on a Tuesday morning in September, seven years after the reunion. "
    "One of our portfolio companies — a logistics software firm — was acquired for forty-seven million dollars.\n\n"
    "I was in a board meeting when the notification came through. I went back to work.\n\n"
    "The acquiring company had an HR onboarding queue that routed new employee approvals through portfolio company investors for the first thirty days post-close. "
    "I had three pending approvals the following week. "
    "One of the names was Frank's.\n\n"
    "He had accepted a regional operations director role through a standard application process. "
    "He had not known the company was in my portfolio. I had not known he had applied.\n\n"
    "I approved the onboarding without delay.\n\n"
    "I also sent a brief welcome note to the new team from the investor side, "
    "the standard message I send for any acquisition — a paragraph about the company's work and our confidence in the team's future.\n\n"
    "I did not mention the reunion. I have not spoken to Frank about it since.\n\n"
    "He has been with the company for fourteen months. I am told he is doing well.\n\n"
    "The consulting was always real. It just needed time to become legible."
  ),
  "broll_keywords": ["startup office", "city skyline", "family gathering", "business meeting", "laptop computer"],
  "hashtags": ["shorts", "storytime", "startup", "family", "statusreversal", "drama"],
  "description": "My uncle called my startup failure out loud at a family reunion. Seven years later he took a job at a company in my portfolio. I approved his onboarding.",
  "estimated_duration": 160,
  "target_duration": 160,
},

{
  "id": "story_071",
  "title": "She Left Partnership Track",
  "genre": "status_reversal",
  "hook": "A colleague said I left partnership track because I ran out of options. Years later I was opposite counsel on the biggest deal of his career.",
  "card_text": '"She left partnership track. That\'s just what you say when you ran out of options." That\'s what my colleague said. So I built my own practice. Years later I was sitting across the table from him with his client asking about my availability.',
  "narration": (
    '"She left partnership track. That\'s just what you say when you ran out of options." '
    "Steven said that to another associate in the kitchen on a Tuesday. "
    "I heard it from the hallway. I continued to my desk.\n\n"
    "I had left the firm three months earlier to build a boutique M&A advisory practice. "
    "It was a deliberate decision, made after I had secured my first retained client and confirmed the model was viable. "
    "I had told no one at the firm except the partner I had worked most closely with, "
    "and I had given full notice and completed every open matter before I left.\n\n"
    "Steven had been a contemporary of mine at the firm. Technically competent, politically careful, "
    "and deeply invested in the premise that the only legitimate career path ran through partnership.\n\n"
    "I built the practice over five years. "
    "I specialized in complex cross-border transactions — the kind that require M&A structuring, regulatory knowledge, and operating company experience "
    "across multiple jurisdictions. The work was detail-intensive and the client relationships were long.\n\n"
    "The transaction that brought us back into contact was Steven's largest engagement to date. "
    "He was representing the seller. I was representing the acquirer.\n\n"
    "I recognized his name in the first representation letter and said nothing to my client.\n\n"
    "We conducted the process professionally over nine months. "
    "Steven was competent. The negotiation was thorough. We closed on time.\n\n"
    "At the final closing session the seller's CEO, who had been watching the process closely, "
    "pulled me aside and asked whether I was taking on new clients. "
    "He had another transaction coming up and wanted to know if I had capacity.\n\n"
    "I handed him a card. Steven was standing nearby.\n\n"
    "He called my office once, the following week. He left a message — something about catching up, "
    "an opening to reconnect. I listened to it, put the phone down, and returned to the term sheet I was reviewing.\n\n"
    "I did not return the call.\n\n"
    "There was no particular satisfaction in that. "
    "The practice was full and the work was good and the client's CEO had already sent an engagement letter.\n\n"
    "I had run out of options at the firm the way a person runs out of options when they find something better. "
    "Steven was still there, working his way through partnership review.\n\n"
    "I hope it goes well for him."
  ),
  "broll_keywords": ["conference room", "legal documents", "city skyline", "business handshake", "modern office"],
  "hashtags": ["shorts", "storytime", "workplace", "career", "statusreversal", "drama"],
  "description": "A colleague said I left partnership track because I ran out of options. Years later his biggest client asked for my card at closing.",
  "estimated_duration": 160,
  "target_duration": 160,
},

]  # end NEW_STORIES


# ─────────────────────────────────────────────────────────────────────────────
# Apply updates
# ─────────────────────────────────────────────────────────────────────────────
def main():
    data = json.loads(STORIES_FILE.read_text())
    stories = data["stories"]

    # Replace existing stories by id
    for i, story in enumerate(stories):
        sid = story.get("id")
        if sid in REWRITES:
            stories[i] = REWRITES[sid]
            print(f"  Rewrote {sid}: {REWRITES[sid]['title']}")

    # Append new stories (only if id not already present)
    existing_ids = {s.get("id") for s in stories}
    for new_story in NEW_STORIES:
        if new_story["id"] not in existing_ids:
            stories.append(new_story)
            print(f"  Added   {new_story['id']}: {new_story['title']}")
        else:
            print(f"  Skipped {new_story['id']} (already present)")

    data["stories"] = stories
    STORIES_FILE.write_text(json.dumps(data, indent=2))
    print(f"\nDone — {len(stories)} total stories in {STORIES_FILE}")


if __name__ == "__main__":
    main()

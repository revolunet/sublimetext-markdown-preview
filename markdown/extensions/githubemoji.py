"""
Github Emoji.

pymdownx.githubemoji
Really simple plugin to add support for
github emojis

MIT license.

Copyright (c) 2014 - 2015 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from ..extensions import Extension
from ..inlinepatterns import Pattern
from .. import util
try:  # pragma: no cover
    import requests
    USE_REQUESTS = True
except Exception:  # pragma: no cover
    USE_REQUESTS = False
import json
import re
import copy

RE_ASSET = re.compile(r'(?P<image>.*?/(?P<name>[^/]+?)\.png)(?:\?(?P<version>.+))?')

# --start--
RE_EMOJI = r'''(?x)
:(
    \+1|\-1|100|1234|8ball|a|ab|abc|abcd|accept|aerial\_tramway|airplane|alarm\_clock|alien|ambulance|anchor|angel
    |anger|angry|anguished|ant|apple|aquarius|aries|arrow\_backward|arrow\_double\_down|arrow\_double\_up
    |arrow\_down|arrow\_down\_small|arrow\_forward|arrow\_heading\_down|arrow\_heading\_up|arrow\_left
    |arrow\_lower\_left|arrow\_lower\_right|arrow\_right|arrow\_right\_hook|arrow\_up|arrow\_up\_down
    |arrow\_up\_small|arrow\_upper\_left|arrow\_upper\_right|arrows\_clockwise|arrows\_counterclockwise|art
    |articulated\_lorry|astonished|athletic\_shoe|atm|b|baby|baby\_bottle|baby\_chick|baby\_symbol|back
    |baggage\_claim|balloon|ballot\_box\_with\_check|bamboo|banana|bangbang|bank|bar\_chart|barber|baseball
    |basketball|bath|bathtub|battery|bear|bee|beer|beers|beetle|beginner|bell|bento|bicyclist|bike|bikini|bird
    |birthday|black\_circle|black\_joker|black\_large\_square|black\_medium\_small\_square|black\_medium\_square
    |black\_nib|black\_small\_square|black\_square\_button|blossom|blowfish|blue\_book|blue\_car|blue\_heart|blush
    |boar|boat|bomb|book|bookmark|bookmark\_tabs|books|boom|boot|bouquet|bow|bowling|bowtie|boy|bread
    |bride\_with\_veil|bridge\_at\_night|briefcase|broken\_heart|bug|bulb|bullettrain\_front|bullettrain\_side|bus
    |busstop|bust\_in\_silhouette|busts\_in\_silhouette|cactus|cake|calendar|calling|camel|camera|cancer|candy
    |capital\_abcd|capricorn|car|card\_index|carousel\_horse|cat|cat2|cd|chart|chart\_with\_downwards\_trend
    |chart\_with\_upwards\_trend|checkered\_flag|cherries|cherry\_blossom|chestnut|chicken|children\_crossing
    |chocolate\_bar|christmas\_tree|church|cinema|circus\_tent|city\_sunrise|city\_sunset|cl|clap|clapper
    |clipboard|clock1|clock10|clock1030|clock11|clock1130|clock12|clock1230|clock130|clock2|clock230|clock3
    |clock330|clock4|clock430|clock5|clock530|clock6|clock630|clock7|clock730|clock8|clock830|clock9|clock930
    |closed\_book|closed\_lock\_with\_key|closed\_umbrella|cloud|clubs|cn|cocktail|coffee|cold\_sweat|collision
    |computer|confetti\_ball|confounded|confused|congratulations|construction|construction\_worker
    |convenience\_store|cookie|cool|cop|copyright|corn|couple|couple\_with\_heart|couplekiss|cow|cow2|credit\_card
    |crescent\_moon|crocodile|crossed\_flags|crown|cry|crying\_cat\_face|crystal\_ball|cupid|curly\_loop
    |currency\_exchange|curry|custard|customs|cyclone|dancer|dancers|dango|dart|dash|date|de|deciduous\_tree
    |department\_store|diamond\_shape\_with\_a\_dot\_inside|diamonds|disappointed|disappointed\_relieved|dizzy
    |dizzy\_face|do\_not\_litter|dog|dog2|dollar|dolls|dolphin|door|doughnut|dragon|dragon\_face|dress
    |dromedary\_camel|droplet|dvd|e\-mail|ear|ear\_of\_rice|earth\_africa|earth\_americas|earth\_asia|egg|eggplant
    |eight|eight\_pointed\_black\_star|eight\_spoked\_asterisk|electric\_plug|elephant|email|end|envelope
    |envelope\_with\_arrow|es|euro|european\_castle|european\_post\_office|evergreen\_tree|exclamation
    |expressionless|eyeglasses|eyes|facepunch|factory|fallen\_leaf|family|fast\_forward|fax|fearful|feelsgood|feet
    |ferris\_wheel|file\_folder|finnadie|fire|fire\_engine|fireworks|first\_quarter\_moon
    |first\_quarter\_moon\_with\_face|fish|fish\_cake|fishing\_pole\_and\_fish|fist|five|flags|flashlight|flipper
    |floppy\_disk|flower\_playing\_cards|flushed|foggy|football|footprints|fork\_and\_knife|fountain|four
    |four\_leaf\_clover|fr|free|fried\_shrimp|fries|frog|frowning|fu|fuelpump|full\_moon|full\_moon\_with\_face
    |game\_die|gb|gem|gemini|ghost|gift|gift\_heart|girl|globe\_with\_meridians|goat|goberserk|godmode|golf|grapes
    |green\_apple|green\_book|green\_heart|grey\_exclamation|grey\_question|grimacing|grin|grinning|guardsman
    |guitar|gun|haircut|hamburger|hammer|hamster|hand|handbag|hankey|hash|hatched\_chick|hatching\_chick
    |headphones|hear\_no\_evil|heart|heart\_decoration|heart\_eyes|heart\_eyes\_cat|heartbeat|heartpulse|hearts
    |heavy\_check\_mark|heavy\_division\_sign|heavy\_dollar\_sign|heavy\_exclamation\_mark|heavy\_minus\_sign
    |heavy\_multiplication\_x|heavy\_plus\_sign|helicopter|herb|hibiscus|high\_brightness|high\_heel|hocho
    |honey\_pot|honeybee|horse|horse\_racing|hospital|hotel|hotsprings|hourglass|hourglass\_flowing\_sand|house
    |house\_with\_garden|hurtrealbad|hushed|ice\_cream|icecream|id|ideograph\_advantage|imp|inbox\_tray
    |incoming\_envelope|information\_desk\_person|information\_source|innocent|interrobang|iphone|it
    |izakaya\_lantern|jack\_o\_lantern|japan|japanese\_castle|japanese\_goblin|japanese\_ogre|jeans|joy|joy\_cat
    |jp|key|keycap\_ten|kimono|kiss|kissing|kissing\_cat|kissing\_closed\_eyes|kissing\_heart
    |kissing\_smiling\_eyes|knife|koala|koko|kr|lantern|large\_blue\_circle|large\_blue\_diamond
    |large\_orange\_diamond|last\_quarter\_moon|last\_quarter\_moon\_with\_face|laughing|leaves|ledger
    |left\_luggage|left\_right\_arrow|leftwards\_arrow\_with\_hook|lemon|leo|leopard|libra|light\_rail|link|lips
    |lipstick|lock|lock\_with\_ink\_pen|lollipop|loop|loud\_sound|loudspeaker|love\_hotel|love\_letter
    |low\_brightness|m|mag|mag\_right|mahjong|mailbox|mailbox\_closed|mailbox\_with\_mail|mailbox\_with\_no\_mail
    |man|man\_with\_gua\_pi\_mao|man\_with\_turban|mans\_shoe|maple\_leaf|mask|massage|meat\_on\_bone|mega|melon
    |memo|mens|metal|metro|microphone|microscope|milky\_way|minibus|minidisc|mobile\_phone\_off|money\_with\_wings
    |moneybag|monkey|monkey\_face|monorail|moon|mortar\_board|mount\_fuji|mountain\_bicyclist|mountain\_cableway
    |mountain\_railway|mouse|mouse2|movie\_camera|moyai|muscle|mushroom|musical\_keyboard|musical\_note
    |musical\_score|mute|nail\_care|name\_badge|neckbeard|necktie|negative\_squared\_cross\_mark|neutral\_face|new
    |new\_moon|new\_moon\_with\_face|newspaper|ng|night\_with\_stars|nine|no\_bell|no\_bicycles|no\_entry
    |no\_entry\_sign|no\_good|no\_mobile\_phones|no\_mouth|no\_pedestrians|no\_smoking|non\-potable\_water|nose
    |notebook|notebook\_with\_decorative\_cover|notes|nut\_and\_bolt|o|o2|ocean|octocat|octopus|oden|office|ok
    |ok\_hand|ok\_woman|older\_man|older\_woman|on|oncoming\_automobile|oncoming\_bus|oncoming\_police\_car
    |oncoming\_taxi|one|open\_book|open\_file\_folder|open\_hands|open\_mouth|ophiuchus|orange\_book|outbox\_tray
    |ox|package|page\_facing\_up|page\_with\_curl|pager|palm\_tree|panda\_face|paperclip|parking
    |part\_alternation\_mark|partly\_sunny|passport\_control|paw\_prints|peach|pear|pencil|pencil2|penguin|pensive
    |performing\_arts|persevere|person\_frowning|person\_with\_blond\_hair|person\_with\_pouting\_face|phone|pig
    |pig2|pig\_nose|pill|pineapple|pisces|pizza|point\_down|point\_left|point\_right|point\_up|point\_up\_2
    |police\_car|poodle|poop|post\_office|postal\_horn|postbox|potable\_water|pouch|poultry\_leg|pound
    |pouting\_cat|pray|princess|punch|purple\_heart|purse|pushpin|put\_litter\_in\_its\_place|question|rabbit
    |rabbit2|racehorse|radio|radio\_button|rage|rage1|rage2|rage3|rage4|railway\_car|rainbow|raised\_hand
    |raised\_hands|raising\_hand|ram|ramen|rat|recycle|red\_car|red\_circle|registered|relaxed|relieved|repeat
    |repeat\_one|restroom|revolving\_hearts|rewind|ribbon|rice|rice\_ball|rice\_cracker|rice\_scene|ring|rocket
    |roller\_coaster|rooster|rose|rotating\_light|round\_pushpin|rowboat|ru|rugby\_football|runner|running
    |running\_shirt\_with\_sash|sa|sagittarius|sailboat|sake|sandal|santa|satellite|satisfied|saxophone|school
    |school\_satchel|scissors|scorpius|scream|scream\_cat|scroll|seat|secret|see\_no\_evil|seedling|seven
    |shaved\_ice|sheep|shell|ship|shipit|shirt|shit|shoe|shower|signal\_strength|six|six\_pointed\_star|ski|skull
    |sleeping|sleepy|slot\_machine|small\_blue\_diamond|small\_orange\_diamond|small\_red\_triangle
    |small\_red\_triangle\_down|smile|smile\_cat|smiley|smiley\_cat|smiling\_imp|smirk|smirk\_cat|smoking|snail
    |snake|snowboarder|snowflake|snowman|sob|soccer|soon|sos|sound|space\_invader|spades|spaghetti|sparkle
    |sparkler|sparkles|sparkling\_heart|speak\_no\_evil|speaker|speech\_balloon|speedboat|squirrel|star|star2
    |stars|station|statue\_of\_liberty|steam\_locomotive|stew|straight\_ruler|strawberry|stuck\_out\_tongue
    |stuck\_out\_tongue\_closed\_eyes|stuck\_out\_tongue\_winking\_eye|sun\_with\_face|sunflower|sunglasses|sunny
    |sunrise|sunrise\_over\_mountains|surfer|sushi|suspect|suspension\_railway|sweat|sweat\_drops|sweat\_smile
    |sweet\_potato|swimmer|symbols|syringe|tada|tanabata\_tree|tangerine|taurus|taxi|tea|telephone
    |telephone\_receiver|telescope|tennis|tent|thought\_balloon|three|thumbsdown|thumbsup|ticket|tiger|tiger2
    |tired\_face|tm|toilet|tokyo\_tower|tomato|tongue|top|tophat|tractor|traffic\_light|train|train2|tram
    |triangular\_flag\_on\_post|triangular\_ruler|trident|triumph|trolleybus|trollface|trophy|tropical\_drink
    |tropical\_fish|truck|trumpet|tshirt|tulip|turtle|tv|twisted\_rightwards\_arrows|two|two\_hearts
    |two\_men\_holding\_hands|two\_women\_holding\_hands|u5272|u5408|u55b6|u6307|u6708|u6709|u6e80|u7121|u7533
    |u7981|u7a7a|uk|umbrella|unamused|underage|unlock|up|us|v|vertical\_traffic\_light|vhs|vibration\_mode
    |video\_camera|video\_game|violin|virgo|volcano|vs|walking|waning\_crescent\_moon|waning\_gibbous\_moon
    |warning|watch|water\_buffalo|watermelon|wave|wavy\_dash|waxing\_crescent\_moon|waxing\_gibbous\_moon|wc|weary
    |wedding|whale|whale2|wheelchair|white\_check\_mark|white\_circle|white\_flower|white\_large\_square
    |white\_medium\_small\_square|white\_medium\_square|white\_small\_square|white\_square\_button|wind\_chime
    |wine\_glass|wink|wolf|woman|womans\_clothes|womans\_hat|womens|worried|wrench|x|yellow\_heart|yen|yum|zap
    |zero|zzz
):'''

URL_EMOJI = {
    "+1": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44d.png",
    "-1": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44e.png",
    "100": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4af.png",
    "1234": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f522.png",
    "8ball": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b1.png",
    "a": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f170.png",
    "ab": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f18e.png",
    "abc": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f524.png",
    "abcd": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f521.png",
    "accept": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f251.png",
    "aerial_tramway": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a1.png",
    "airplane": "https://assets-cdn.github.com/images/icons/emoji/unicode/2708.png",
    "alarm_clock": "https://assets-cdn.github.com/images/icons/emoji/unicode/23f0.png",
    "alien": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f47d.png",
    "ambulance": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f691.png",
    "anchor": "https://assets-cdn.github.com/images/icons/emoji/unicode/2693.png",
    "angel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f47c.png",
    "anger": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a2.png",
    "angry": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f620.png",
    "anguished": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f627.png",
    "ant": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41c.png",
    "apple": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f34e.png",
    "aquarius": "https://assets-cdn.github.com/images/icons/emoji/unicode/2652.png",
    "aries": "https://assets-cdn.github.com/images/icons/emoji/unicode/2648.png",
    "arrow_backward": "https://assets-cdn.github.com/images/icons/emoji/unicode/25c0.png",
    "arrow_double_down": "https://assets-cdn.github.com/images/icons/emoji/unicode/23ec.png",
    "arrow_double_up": "https://assets-cdn.github.com/images/icons/emoji/unicode/23eb.png",
    "arrow_down": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b07.png",
    "arrow_down_small": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f53d.png",
    "arrow_forward": "https://assets-cdn.github.com/images/icons/emoji/unicode/25b6.png",
    "arrow_heading_down": "https://assets-cdn.github.com/images/icons/emoji/unicode/2935.png",
    "arrow_heading_up": "https://assets-cdn.github.com/images/icons/emoji/unicode/2934.png",
    "arrow_left": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b05.png",
    "arrow_lower_left": "https://assets-cdn.github.com/images/icons/emoji/unicode/2199.png",
    "arrow_lower_right": "https://assets-cdn.github.com/images/icons/emoji/unicode/2198.png",
    "arrow_right": "https://assets-cdn.github.com/images/icons/emoji/unicode/27a1.png",
    "arrow_right_hook": "https://assets-cdn.github.com/images/icons/emoji/unicode/21aa.png",
    "arrow_up": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b06.png",
    "arrow_up_down": "https://assets-cdn.github.com/images/icons/emoji/unicode/2195.png",
    "arrow_up_small": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f53c.png",
    "arrow_upper_left": "https://assets-cdn.github.com/images/icons/emoji/unicode/2196.png",
    "arrow_upper_right": "https://assets-cdn.github.com/images/icons/emoji/unicode/2197.png",
    "arrows_clockwise": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f503.png",
    "arrows_counterclockwise": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f504.png",
    "art": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a8.png",
    "articulated_lorry": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f69b.png",
    "astonished": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f632.png",
    "athletic_shoe": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45f.png",
    "atm": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e7.png",
    "b": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f171.png",
    "baby": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f476.png",
    "baby_bottle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f37c.png",
    "baby_chick": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f424.png",
    "baby_symbol": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6bc.png",
    "back": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f519.png",
    "baggage_claim": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6c4.png",
    "balloon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f388.png",
    "ballot_box_with_check": "https://assets-cdn.github.com/images/icons/emoji/unicode/2611.png",
    "bamboo": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f38d.png",
    "banana": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f34c.png",
    "bangbang": "https://assets-cdn.github.com/images/icons/emoji/unicode/203c.png",
    "bank": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e6.png",
    "bar_chart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ca.png",
    "barber": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f488.png",
    "baseball": "https://assets-cdn.github.com/images/icons/emoji/unicode/26be.png",
    "basketball": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c0.png",
    "bath": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6c0.png",
    "bathtub": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6c1.png",
    "battery": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f50b.png",
    "bear": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f43b.png",
    "bee": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41d.png",
    "beer": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f37a.png",
    "beers": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f37b.png",
    "beetle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41e.png",
    "beginner": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f530.png",
    "bell": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f514.png",
    "bento": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f371.png",
    "bicyclist": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b4.png",
    "bike": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b2.png",
    "bikini": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f459.png",
    "bird": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f426.png",
    "birthday": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f382.png",
    "black_circle": "https://assets-cdn.github.com/images/icons/emoji/unicode/26ab.png",
    "black_joker": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f0cf.png",
    "black_large_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b1b.png",
    "black_medium_small_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/25fe.png",
    "black_medium_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/25fc.png",
    "black_nib": "https://assets-cdn.github.com/images/icons/emoji/unicode/2712.png",
    "black_small_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/25aa.png",
    "black_square_button": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f532.png",
    "blossom": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f33c.png",
    "blowfish": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f421.png",
    "blue_book": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d8.png",
    "blue_car": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f699.png",
    "blue_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f499.png",
    "blush": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f60a.png",
    "boar": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f417.png",
    "boat": "https://assets-cdn.github.com/images/icons/emoji/unicode/26f5.png",
    "bomb": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a3.png",
    "book": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d6.png",
    "bookmark": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f516.png",
    "bookmark_tabs": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d1.png",
    "books": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4da.png",
    "boom": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a5.png",
    "boot": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f462.png",
    "bouquet": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f490.png",
    "bow": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f647.png",
    "bowling": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b3.png",
    "bowtie": "https://assets-cdn.github.com/images/icons/emoji/bowtie.png",
    "boy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f466.png",
    "bread": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f35e.png",
    "bride_with_veil": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f470.png",
    "bridge_at_night": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f309.png",
    "briefcase": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4bc.png",
    "broken_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f494.png",
    "bug": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41b.png",
    "bulb": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a1.png",
    "bullettrain_front": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f685.png",
    "bullettrain_side": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f684.png",
    "bus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f68c.png",
    "busstop": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f68f.png",
    "bust_in_silhouette": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f464.png",
    "busts_in_silhouette": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f465.png",
    "cactus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f335.png",
    "cake": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f370.png",
    "calendar": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c6.png",
    "calling": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f2.png",
    "camel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42b.png",
    "camera": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f7.png",
    "cancer": "https://assets-cdn.github.com/images/icons/emoji/unicode/264b.png",
    "candy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f36c.png",
    "capital_abcd": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f520.png",
    "capricorn": "https://assets-cdn.github.com/images/icons/emoji/unicode/2651.png",
    "car": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f697.png",
    "card_index": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c7.png",
    "carousel_horse": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a0.png",
    "cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f431.png",
    "cat2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f408.png",
    "cd": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4bf.png",
    "chart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b9.png",
    "chart_with_downwards_trend": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c9.png",
    "chart_with_upwards_trend": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c8.png",
    "checkered_flag": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c1.png",
    "cherries": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f352.png",
    "cherry_blossom": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f338.png",
    "chestnut": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f330.png",
    "chicken": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f414.png",
    "children_crossing": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b8.png",
    "chocolate_bar": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f36b.png",
    "christmas_tree": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f384.png",
    "church": "https://assets-cdn.github.com/images/icons/emoji/unicode/26ea.png",
    "cinema": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a6.png",
    "circus_tent": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3aa.png",
    "city_sunrise": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f307.png",
    "city_sunset": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f306.png",
    "cl": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f191.png",
    "clap": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44f.png",
    "clapper": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ac.png",
    "clipboard": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4cb.png",
    "clock1": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f550.png",
    "clock10": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f559.png",
    "clock1030": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f565.png",
    "clock11": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f55a.png",
    "clock1130": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f566.png",
    "clock12": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f55b.png",
    "clock1230": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f567.png",
    "clock130": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f55c.png",
    "clock2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f551.png",
    "clock230": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f55d.png",
    "clock3": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f552.png",
    "clock330": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f55e.png",
    "clock4": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f553.png",
    "clock430": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f55f.png",
    "clock5": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f554.png",
    "clock530": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f560.png",
    "clock6": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f555.png",
    "clock630": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f561.png",
    "clock7": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f556.png",
    "clock730": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f562.png",
    "clock8": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f557.png",
    "clock830": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f563.png",
    "clock9": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f558.png",
    "clock930": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f564.png",
    "closed_book": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d5.png",
    "closed_lock_with_key": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f510.png",
    "closed_umbrella": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f302.png",
    "cloud": "https://assets-cdn.github.com/images/icons/emoji/unicode/2601.png",
    "clubs": "https://assets-cdn.github.com/images/icons/emoji/unicode/2663.png",
    "cn": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1e8-1f1f3.png",
    "cocktail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f378.png",
    "coffee": "https://assets-cdn.github.com/images/icons/emoji/unicode/2615.png",
    "cold_sweat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f630.png",
    "collision": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a5.png",
    "computer": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4bb.png",
    "confetti_ball": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f38a.png",
    "confounded": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f616.png",
    "confused": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f615.png",
    "congratulations": "https://assets-cdn.github.com/images/icons/emoji/unicode/3297.png",
    "construction": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a7.png",
    "construction_worker": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f477.png",
    "convenience_store": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ea.png",
    "cookie": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f36a.png",
    "cool": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f192.png",
    "cop": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f46e.png",
    "copyright": "https://assets-cdn.github.com/images/icons/emoji/unicode/00a9.png",
    "corn": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f33d.png",
    "couple": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f46b.png",
    "couple_with_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f491.png",
    "couplekiss": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f48f.png",
    "cow": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42e.png",
    "cow2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f404.png",
    "credit_card": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b3.png",
    "crescent_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f319.png",
    "crocodile": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f40a.png",
    "crossed_flags": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f38c.png",
    "crown": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f451.png",
    "cry": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f622.png",
    "crying_cat_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f63f.png",
    "crystal_ball": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52e.png",
    "cupid": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f498.png",
    "curly_loop": "https://assets-cdn.github.com/images/icons/emoji/unicode/27b0.png",
    "currency_exchange": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b1.png",
    "curry": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f35b.png",
    "custard": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f36e.png",
    "customs": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6c3.png",
    "cyclone": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f300.png",
    "dancer": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f483.png",
    "dancers": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f46f.png",
    "dango": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f361.png",
    "dart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3af.png",
    "dash": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a8.png",
    "date": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c5.png",
    "de": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1e9-1f1ea.png",
    "deciduous_tree": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f333.png",
    "department_store": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ec.png",
    "diamond_shape_with_a_dot_inside": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a0.png",
    "diamonds": "https://assets-cdn.github.com/images/icons/emoji/unicode/2666.png",
    "disappointed": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f61e.png",
    "disappointed_relieved": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f625.png",
    "dizzy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ab.png",
    "dizzy_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f635.png",
    "do_not_litter": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6af.png",
    "dog": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f436.png",
    "dog2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f415.png",
    "dollar": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b5.png",
    "dolls": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f38e.png",
    "dolphin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42c.png",
    "door": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6aa.png",
    "doughnut": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f369.png",
    "dragon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f409.png",
    "dragon_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f432.png",
    "dress": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f457.png",
    "dromedary_camel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42a.png",
    "droplet": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a7.png",
    "dvd": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c0.png",
    "e-mail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e7.png",
    "ear": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f442.png",
    "ear_of_rice": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f33e.png",
    "earth_africa": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f30d.png",
    "earth_americas": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f30e.png",
    "earth_asia": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f30f.png",
    "egg": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f373.png",
    "eggplant": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f346.png",
    "eight": "https://assets-cdn.github.com/images/icons/emoji/unicode/0038-20e3.png",
    "eight_pointed_black_star": "https://assets-cdn.github.com/images/icons/emoji/unicode/2734.png",
    "eight_spoked_asterisk": "https://assets-cdn.github.com/images/icons/emoji/unicode/2733.png",
    "electric_plug": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f50c.png",
    "elephant": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f418.png",
    "email": "https://assets-cdn.github.com/images/icons/emoji/unicode/2709.png",
    "end": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f51a.png",
    "envelope": "https://assets-cdn.github.com/images/icons/emoji/unicode/2709.png",
    "envelope_with_arrow": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e9.png",
    "es": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1ea-1f1f8.png",
    "euro": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b6.png",
    "european_castle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3f0.png",
    "european_post_office": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e4.png",
    "evergreen_tree": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f332.png",
    "exclamation": "https://assets-cdn.github.com/images/icons/emoji/unicode/2757.png",
    "expressionless": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f611.png",
    "eyeglasses": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f453.png",
    "eyes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f440.png",
    "facepunch": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44a.png",
    "factory": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ed.png",
    "fallen_leaf": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f342.png",
    "family": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f46a.png",
    "fast_forward": "https://assets-cdn.github.com/images/icons/emoji/unicode/23e9.png",
    "fax": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e0.png",
    "fearful": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f628.png",
    "feelsgood": "https://assets-cdn.github.com/images/icons/emoji/feelsgood.png",
    "feet": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f43e.png",
    "ferris_wheel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a1.png",
    "file_folder": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c1.png",
    "finnadie": "https://assets-cdn.github.com/images/icons/emoji/finnadie.png",
    "fire": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f525.png",
    "fire_engine": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f692.png",
    "fireworks": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f386.png",
    "first_quarter_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f313.png",
    "first_quarter_moon_with_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f31b.png",
    "fish": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41f.png",
    "fish_cake": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f365.png",
    "fishing_pole_and_fish": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a3.png",
    "fist": "https://assets-cdn.github.com/images/icons/emoji/unicode/270a.png",
    "five": "https://assets-cdn.github.com/images/icons/emoji/unicode/0035-20e3.png",
    "flags": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f38f.png",
    "flashlight": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f526.png",
    "flipper": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42c.png",
    "floppy_disk": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4be.png",
    "flower_playing_cards": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b4.png",
    "flushed": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f633.png",
    "foggy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f301.png",
    "football": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c8.png",
    "footprints": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f463.png",
    "fork_and_knife": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f374.png",
    "fountain": "https://assets-cdn.github.com/images/icons/emoji/unicode/26f2.png",
    "four": "https://assets-cdn.github.com/images/icons/emoji/unicode/0034-20e3.png",
    "four_leaf_clover": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f340.png",
    "fr": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1eb-1f1f7.png",
    "free": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f193.png",
    "fried_shrimp": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f364.png",
    "fries": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f35f.png",
    "frog": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f438.png",
    "frowning": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f626.png",
    "fu": "https://assets-cdn.github.com/images/icons/emoji/fu.png",
    "fuelpump": "https://assets-cdn.github.com/images/icons/emoji/unicode/26fd.png",
    "full_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f315.png",
    "full_moon_with_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f31d.png",
    "game_die": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b2.png",
    "gb": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1ec-1f1e7.png",
    "gem": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f48e.png",
    "gemini": "https://assets-cdn.github.com/images/icons/emoji/unicode/264a.png",
    "ghost": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f47b.png",
    "gift": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f381.png",
    "gift_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f49d.png",
    "girl": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f467.png",
    "globe_with_meridians": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f310.png",
    "goat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f410.png",
    "goberserk": "https://assets-cdn.github.com/images/icons/emoji/goberserk.png",
    "godmode": "https://assets-cdn.github.com/images/icons/emoji/godmode.png",
    "golf": "https://assets-cdn.github.com/images/icons/emoji/unicode/26f3.png",
    "grapes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f347.png",
    "green_apple": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f34f.png",
    "green_book": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d7.png",
    "green_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f49a.png",
    "grey_exclamation": "https://assets-cdn.github.com/images/icons/emoji/unicode/2755.png",
    "grey_question": "https://assets-cdn.github.com/images/icons/emoji/unicode/2754.png",
    "grimacing": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f62c.png",
    "grin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f601.png",
    "grinning": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f600.png",
    "guardsman": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f482.png",
    "guitar": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b8.png",
    "gun": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52b.png",
    "haircut": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f487.png",
    "hamburger": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f354.png",
    "hammer": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f528.png",
    "hamster": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f439.png",
    "hand": "https://assets-cdn.github.com/images/icons/emoji/unicode/270b.png",
    "handbag": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45c.png",
    "hankey": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a9.png",
    "hash": "https://assets-cdn.github.com/images/icons/emoji/unicode/0023-20e3.png",
    "hatched_chick": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f425.png",
    "hatching_chick": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f423.png",
    "headphones": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a7.png",
    "hear_no_evil": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f649.png",
    "heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/2764.png",
    "heart_decoration": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f49f.png",
    "heart_eyes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f60d.png",
    "heart_eyes_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f63b.png",
    "heartbeat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f493.png",
    "heartpulse": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f497.png",
    "hearts": "https://assets-cdn.github.com/images/icons/emoji/unicode/2665.png",
    "heavy_check_mark": "https://assets-cdn.github.com/images/icons/emoji/unicode/2714.png",
    "heavy_division_sign": "https://assets-cdn.github.com/images/icons/emoji/unicode/2797.png",
    "heavy_dollar_sign": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b2.png",
    "heavy_exclamation_mark": "https://assets-cdn.github.com/images/icons/emoji/unicode/2757.png",
    "heavy_minus_sign": "https://assets-cdn.github.com/images/icons/emoji/unicode/2796.png",
    "heavy_multiplication_x": "https://assets-cdn.github.com/images/icons/emoji/unicode/2716.png",
    "heavy_plus_sign": "https://assets-cdn.github.com/images/icons/emoji/unicode/2795.png",
    "helicopter": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f681.png",
    "herb": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f33f.png",
    "hibiscus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f33a.png",
    "high_brightness": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f506.png",
    "high_heel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f460.png",
    "hocho": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52a.png",
    "honey_pot": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f36f.png",
    "honeybee": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41d.png",
    "horse": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f434.png",
    "horse_racing": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c7.png",
    "hospital": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e5.png",
    "hotel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e8.png",
    "hotsprings": "https://assets-cdn.github.com/images/icons/emoji/unicode/2668.png",
    "hourglass": "https://assets-cdn.github.com/images/icons/emoji/unicode/231b.png",
    "hourglass_flowing_sand": "https://assets-cdn.github.com/images/icons/emoji/unicode/23f3.png",
    "house": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e0.png",
    "house_with_garden": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e1.png",
    "hurtrealbad": "https://assets-cdn.github.com/images/icons/emoji/hurtrealbad.png",
    "hushed": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f62f.png",
    "ice_cream": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f368.png",
    "icecream": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f366.png",
    "id": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f194.png",
    "ideograph_advantage": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f250.png",
    "imp": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f47f.png",
    "inbox_tray": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e5.png",
    "incoming_envelope": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e8.png",
    "information_desk_person": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f481.png",
    "information_source": "https://assets-cdn.github.com/images/icons/emoji/unicode/2139.png",
    "innocent": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f607.png",
    "interrobang": "https://assets-cdn.github.com/images/icons/emoji/unicode/2049.png",
    "iphone": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f1.png",
    "it": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1ee-1f1f9.png",
    "izakaya_lantern": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ee.png",
    "jack_o_lantern": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f383.png",
    "japan": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f5fe.png",
    "japanese_castle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ef.png",
    "japanese_goblin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f47a.png",
    "japanese_ogre": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f479.png",
    "jeans": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f456.png",
    "joy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f602.png",
    "joy_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f639.png",
    "jp": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1ef-1f1f5.png",
    "key": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f511.png",
    "keycap_ten": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f51f.png",
    "kimono": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f458.png",
    "kiss": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f48b.png",
    "kissing": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f617.png",
    "kissing_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f63d.png",
    "kissing_closed_eyes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f61a.png",
    "kissing_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f618.png",
    "kissing_smiling_eyes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f619.png",
    "knife": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52a.png",
    "koala": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f428.png",
    "koko": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f201.png",
    "kr": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1f0-1f1f7.png",
    "lantern": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ee.png",
    "large_blue_circle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f535.png",
    "large_blue_diamond": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f537.png",
    "large_orange_diamond": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f536.png",
    "last_quarter_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f317.png",
    "last_quarter_moon_with_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f31c.png",
    "laughing": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f606.png",
    "leaves": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f343.png",
    "ledger": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d2.png",
    "left_luggage": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6c5.png",
    "left_right_arrow": "https://assets-cdn.github.com/images/icons/emoji/unicode/2194.png",
    "leftwards_arrow_with_hook": "https://assets-cdn.github.com/images/icons/emoji/unicode/21a9.png",
    "lemon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f34b.png",
    "leo": "https://assets-cdn.github.com/images/icons/emoji/unicode/264c.png",
    "leopard": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f406.png",
    "libra": "https://assets-cdn.github.com/images/icons/emoji/unicode/264e.png",
    "light_rail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f688.png",
    "link": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f517.png",
    "lips": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f444.png",
    "lipstick": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f484.png",
    "lock": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f512.png",
    "lock_with_ink_pen": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f50f.png",
    "lollipop": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f36d.png",
    "loop": "https://assets-cdn.github.com/images/icons/emoji/unicode/27bf.png",
    "loud_sound": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f50a.png",
    "loudspeaker": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e2.png",
    "love_hotel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e9.png",
    "love_letter": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f48c.png",
    "low_brightness": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f505.png",
    "m": "https://assets-cdn.github.com/images/icons/emoji/unicode/24c2.png",
    "mag": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f50d.png",
    "mag_right": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f50e.png",
    "mahjong": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f004.png",
    "mailbox": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4eb.png",
    "mailbox_closed": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ea.png",
    "mailbox_with_mail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ec.png",
    "mailbox_with_no_mail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ed.png",
    "man": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f468.png",
    "man_with_gua_pi_mao": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f472.png",
    "man_with_turban": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f473.png",
    "mans_shoe": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45e.png",
    "maple_leaf": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f341.png",
    "mask": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f637.png",
    "massage": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f486.png",
    "meat_on_bone": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f356.png",
    "mega": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e3.png",
    "melon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f348.png",
    "memo": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4dd.png",
    "mens": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b9.png",
    "metal": "https://assets-cdn.github.com/images/icons/emoji/metal.png",
    "metro": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f687.png",
    "microphone": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a4.png",
    "microscope": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52c.png",
    "milky_way": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f30c.png",
    "minibus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f690.png",
    "minidisc": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4bd.png",
    "mobile_phone_off": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f4.png",
    "money_with_wings": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b8.png",
    "moneybag": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b0.png",
    "monkey": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f412.png",
    "monkey_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f435.png",
    "monorail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f69d.png",
    "moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f314.png",
    "mortar_board": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f393.png",
    "mount_fuji": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f5fb.png",
    "mountain_bicyclist": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b5.png",
    "mountain_cableway": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a0.png",
    "mountain_railway": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f69e.png",
    "mouse": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42d.png",
    "mouse2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f401.png",
    "movie_camera": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a5.png",
    "moyai": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f5ff.png",
    "muscle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4aa.png",
    "mushroom": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f344.png",
    "musical_keyboard": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b9.png",
    "musical_note": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b5.png",
    "musical_score": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3bc.png",
    "mute": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f507.png",
    "nail_care": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f485.png",
    "name_badge": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4db.png",
    "neckbeard": "https://assets-cdn.github.com/images/icons/emoji/neckbeard.png",
    "necktie": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f454.png",
    "negative_squared_cross_mark": "https://assets-cdn.github.com/images/icons/emoji/unicode/274e.png",
    "neutral_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f610.png",
    "new": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f195.png",
    "new_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f311.png",
    "new_moon_with_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f31a.png",
    "newspaper": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f0.png",
    "ng": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f196.png",
    "night_with_stars": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f303.png",
    "nine": "https://assets-cdn.github.com/images/icons/emoji/unicode/0039-20e3.png",
    "no_bell": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f515.png",
    "no_bicycles": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b3.png",
    "no_entry": "https://assets-cdn.github.com/images/icons/emoji/unicode/26d4.png",
    "no_entry_sign": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6ab.png",
    "no_good": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f645.png",
    "no_mobile_phones": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f5.png",
    "no_mouth": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f636.png",
    "no_pedestrians": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b7.png",
    "no_smoking": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6ad.png",
    "non-potable_water": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b1.png",
    "nose": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f443.png",
    "notebook": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d3.png",
    "notebook_with_decorative_cover": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d4.png",
    "notes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b6.png",
    "nut_and_bolt": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f529.png",
    "o": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b55.png",
    "o2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f17e.png",
    "ocean": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f30a.png",
    "octocat": "https://assets-cdn.github.com/images/icons/emoji/octocat.png",
    "octopus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f419.png",
    "oden": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f362.png",
    "office": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e2.png",
    "ok": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f197.png",
    "ok_hand": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44c.png",
    "ok_woman": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f646.png",
    "older_man": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f474.png",
    "older_woman": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f475.png",
    "on": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f51b.png",
    "oncoming_automobile": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f698.png",
    "oncoming_bus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f68d.png",
    "oncoming_police_car": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f694.png",
    "oncoming_taxi": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f696.png",
    "one": "https://assets-cdn.github.com/images/icons/emoji/unicode/0031-20e3.png",
    "open_book": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d6.png",
    "open_file_folder": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c2.png",
    "open_hands": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f450.png",
    "open_mouth": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f62e.png",
    "ophiuchus": "https://assets-cdn.github.com/images/icons/emoji/unicode/26ce.png",
    "orange_book": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d9.png",
    "outbox_tray": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e4.png",
    "ox": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f402.png",
    "package": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e6.png",
    "page_facing_up": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c4.png",
    "page_with_curl": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4c3.png",
    "pager": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4df.png",
    "palm_tree": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f334.png",
    "panda_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f43c.png",
    "paperclip": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ce.png",
    "parking": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f17f.png",
    "part_alternation_mark": "https://assets-cdn.github.com/images/icons/emoji/unicode/303d.png",
    "partly_sunny": "https://assets-cdn.github.com/images/icons/emoji/unicode/26c5.png",
    "passport_control": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6c2.png",
    "paw_prints": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f43e.png",
    "peach": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f351.png",
    "pear": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f350.png",
    "pencil": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4dd.png",
    "pencil2": "https://assets-cdn.github.com/images/icons/emoji/unicode/270f.png",
    "penguin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f427.png",
    "pensive": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f614.png",
    "performing_arts": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ad.png",
    "persevere": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f623.png",
    "person_frowning": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f64d.png",
    "person_with_blond_hair": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f471.png",
    "person_with_pouting_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f64e.png",
    "phone": "https://assets-cdn.github.com/images/icons/emoji/unicode/260e.png",
    "pig": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f437.png",
    "pig2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f416.png",
    "pig_nose": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f43d.png",
    "pill": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f48a.png",
    "pineapple": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f34d.png",
    "pisces": "https://assets-cdn.github.com/images/icons/emoji/unicode/2653.png",
    "pizza": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f355.png",
    "point_down": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f447.png",
    "point_left": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f448.png",
    "point_right": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f449.png",
    "point_up": "https://assets-cdn.github.com/images/icons/emoji/unicode/261d.png",
    "point_up_2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f446.png",
    "police_car": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f693.png",
    "poodle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f429.png",
    "poop": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a9.png",
    "post_office": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3e3.png",
    "postal_horn": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ef.png",
    "postbox": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ee.png",
    "potable_water": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b0.png",
    "pouch": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45d.png",
    "poultry_leg": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f357.png",
    "pound": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b7.png",
    "pouting_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f63e.png",
    "pray": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f64f.png",
    "princess": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f478.png",
    "punch": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44a.png",
    "purple_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f49c.png",
    "purse": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45b.png",
    "pushpin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4cc.png",
    "put_litter_in_its_place": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6ae.png",
    "question": "https://assets-cdn.github.com/images/icons/emoji/unicode/2753.png",
    "rabbit": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f430.png",
    "rabbit2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f407.png",
    "racehorse": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f40e.png",
    "radio": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4fb.png",
    "radio_button": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f518.png",
    "rage": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f621.png",
    "rage1": "https://assets-cdn.github.com/images/icons/emoji/rage1.png",
    "rage2": "https://assets-cdn.github.com/images/icons/emoji/rage2.png",
    "rage3": "https://assets-cdn.github.com/images/icons/emoji/rage3.png",
    "rage4": "https://assets-cdn.github.com/images/icons/emoji/rage4.png",
    "railway_car": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f683.png",
    "rainbow": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f308.png",
    "raised_hand": "https://assets-cdn.github.com/images/icons/emoji/unicode/270b.png",
    "raised_hands": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f64c.png",
    "raising_hand": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f64b.png",
    "ram": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f40f.png",
    "ramen": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f35c.png",
    "rat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f400.png",
    "recycle": "https://assets-cdn.github.com/images/icons/emoji/unicode/267b.png",
    "red_car": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f697.png",
    "red_circle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f534.png",
    "registered": "https://assets-cdn.github.com/images/icons/emoji/unicode/00ae.png",
    "relaxed": "https://assets-cdn.github.com/images/icons/emoji/unicode/263a.png",
    "relieved": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f60c.png",
    "repeat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f501.png",
    "repeat_one": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f502.png",
    "restroom": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6bb.png",
    "revolving_hearts": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f49e.png",
    "rewind": "https://assets-cdn.github.com/images/icons/emoji/unicode/23ea.png",
    "ribbon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f380.png",
    "rice": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f35a.png",
    "rice_ball": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f359.png",
    "rice_cracker": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f358.png",
    "rice_scene": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f391.png",
    "ring": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f48d.png",
    "rocket": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f680.png",
    "roller_coaster": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a2.png",
    "rooster": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f413.png",
    "rose": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f339.png",
    "rotating_light": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a8.png",
    "round_pushpin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4cd.png",
    "rowboat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a3.png",
    "ru": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1f7-1f1fa.png",
    "rugby_football": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c9.png",
    "runner": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c3.png",
    "running": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c3.png",
    "running_shirt_with_sash": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3bd.png",
    "sa": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f202.png",
    "sagittarius": "https://assets-cdn.github.com/images/icons/emoji/unicode/2650.png",
    "sailboat": "https://assets-cdn.github.com/images/icons/emoji/unicode/26f5.png",
    "sake": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f376.png",
    "sandal": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f461.png",
    "santa": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f385.png",
    "satellite": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4e1.png",
    "satisfied": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f606.png",
    "saxophone": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b7.png",
    "school": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3eb.png",
    "school_satchel": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f392.png",
    "scissors": "https://assets-cdn.github.com/images/icons/emoji/unicode/2702.png",
    "scorpius": "https://assets-cdn.github.com/images/icons/emoji/unicode/264f.png",
    "scream": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f631.png",
    "scream_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f640.png",
    "scroll": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4dc.png",
    "seat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ba.png",
    "secret": "https://assets-cdn.github.com/images/icons/emoji/unicode/3299.png",
    "see_no_evil": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f648.png",
    "seedling": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f331.png",
    "seven": "https://assets-cdn.github.com/images/icons/emoji/unicode/0037-20e3.png",
    "shaved_ice": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f367.png",
    "sheep": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f411.png",
    "shell": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f41a.png",
    "ship": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a2.png",
    "shipit": "https://assets-cdn.github.com/images/icons/emoji/shipit.png",
    "shirt": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f455.png",
    "shit": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a9.png",
    "shoe": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45e.png",
    "shower": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6bf.png",
    "signal_strength": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f6.png",
    "six": "https://assets-cdn.github.com/images/icons/emoji/unicode/0036-20e3.png",
    "six_pointed_star": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52f.png",
    "ski": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3bf.png",
    "skull": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f480.png",
    "sleeping": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f634.png",
    "sleepy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f62a.png",
    "slot_machine": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3b0.png",
    "small_blue_diamond": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f539.png",
    "small_orange_diamond": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f538.png",
    "small_red_triangle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f53a.png",
    "small_red_triangle_down": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f53b.png",
    "smile": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f604.png",
    "smile_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f638.png",
    "smiley": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f603.png",
    "smiley_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f63a.png",
    "smiling_imp": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f608.png",
    "smirk": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f60f.png",
    "smirk_cat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f63c.png",
    "smoking": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6ac.png",
    "snail": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f40c.png",
    "snake": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f40d.png",
    "snowboarder": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c2.png",
    "snowflake": "https://assets-cdn.github.com/images/icons/emoji/unicode/2744.png",
    "snowman": "https://assets-cdn.github.com/images/icons/emoji/unicode/26c4.png",
    "sob": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f62d.png",
    "soccer": "https://assets-cdn.github.com/images/icons/emoji/unicode/26bd.png",
    "soon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f51c.png",
    "sos": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f198.png",
    "sound": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f509.png",
    "space_invader": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f47e.png",
    "spades": "https://assets-cdn.github.com/images/icons/emoji/unicode/2660.png",
    "spaghetti": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f35d.png",
    "sparkle": "https://assets-cdn.github.com/images/icons/emoji/unicode/2747.png",
    "sparkler": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f387.png",
    "sparkles": "https://assets-cdn.github.com/images/icons/emoji/unicode/2728.png",
    "sparkling_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f496.png",
    "speak_no_evil": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f64a.png",
    "speaker": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f508.png",
    "speech_balloon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ac.png",
    "speedboat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a4.png",
    "squirrel": "https://assets-cdn.github.com/images/icons/emoji/shipit.png",
    "star": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b50.png",
    "star2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f31f.png",
    "stars": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f320.png",
    "station": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f689.png",
    "statue_of_liberty": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f5fd.png",
    "steam_locomotive": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f682.png",
    "stew": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f372.png",
    "straight_ruler": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4cf.png",
    "strawberry": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f353.png",
    "stuck_out_tongue": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f61b.png",
    "stuck_out_tongue_closed_eyes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f61d.png",
    "stuck_out_tongue_winking_eye": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f61c.png",
    "sun_with_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f31e.png",
    "sunflower": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f33b.png",
    "sunglasses": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f60e.png",
    "sunny": "https://assets-cdn.github.com/images/icons/emoji/unicode/2600.png",
    "sunrise": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f305.png",
    "sunrise_over_mountains": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f304.png",
    "surfer": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c4.png",
    "sushi": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f363.png",
    "suspect": "https://assets-cdn.github.com/images/icons/emoji/suspect.png",
    "suspension_railway": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f69f.png",
    "sweat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f613.png",
    "sweat_drops": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a6.png",
    "sweat_smile": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f605.png",
    "sweet_potato": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f360.png",
    "swimmer": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ca.png",
    "symbols": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f523.png",
    "syringe": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f489.png",
    "tada": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f389.png",
    "tanabata_tree": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f38b.png",
    "tangerine": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f34a.png",
    "taurus": "https://assets-cdn.github.com/images/icons/emoji/unicode/2649.png",
    "taxi": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f695.png",
    "tea": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f375.png",
    "telephone": "https://assets-cdn.github.com/images/icons/emoji/unicode/260e.png",
    "telephone_receiver": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4de.png",
    "telescope": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f52d.png",
    "tennis": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3be.png",
    "tent": "https://assets-cdn.github.com/images/icons/emoji/unicode/26fa.png",
    "thought_balloon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ad.png",
    "three": "https://assets-cdn.github.com/images/icons/emoji/unicode/0033-20e3.png",
    "thumbsdown": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44e.png",
    "thumbsup": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44d.png",
    "ticket": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ab.png",
    "tiger": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f42f.png",
    "tiger2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f405.png",
    "tired_face": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f62b.png",
    "tm": "https://assets-cdn.github.com/images/icons/emoji/unicode/2122.png",
    "toilet": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6bd.png",
    "tokyo_tower": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f5fc.png",
    "tomato": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f345.png",
    "tongue": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f445.png",
    "top": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f51d.png",
    "tophat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3a9.png",
    "tractor": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f69c.png",
    "traffic_light": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a5.png",
    "train": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f68b.png",
    "train2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f686.png",
    "tram": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f68a.png",
    "triangular_flag_on_post": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a9.png",
    "triangular_ruler": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4d0.png",
    "trident": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f531.png",
    "triumph": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f624.png",
    "trolleybus": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f68e.png",
    "trollface": "https://assets-cdn.github.com/images/icons/emoji/trollface.png",
    "trophy": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3c6.png",
    "tropical_drink": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f379.png",
    "tropical_fish": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f420.png",
    "truck": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f69a.png",
    "trumpet": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ba.png",
    "tshirt": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f455.png",
    "tulip": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f337.png",
    "turtle": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f422.png",
    "tv": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4fa.png",
    "twisted_rightwards_arrows": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f500.png",
    "two": "https://assets-cdn.github.com/images/icons/emoji/unicode/0032-20e3.png",
    "two_hearts": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f495.png",
    "two_men_holding_hands": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f46c.png",
    "two_women_holding_hands": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f46d.png",
    "u5272": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f239.png",
    "u5408": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f234.png",
    "u55b6": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f23a.png",
    "u6307": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f22f.png",
    "u6708": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f237.png",
    "u6709": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f236.png",
    "u6e80": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f235.png",
    "u7121": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f21a.png",
    "u7533": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f238.png",
    "u7981": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f232.png",
    "u7a7a": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f233.png",
    "uk": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1ec-1f1e7.png",
    "umbrella": "https://assets-cdn.github.com/images/icons/emoji/unicode/2614.png",
    "unamused": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f612.png",
    "underage": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f51e.png",
    "unlock": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f513.png",
    "up": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f199.png",
    "us": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f1fa-1f1f8.png",
    "v": "https://assets-cdn.github.com/images/icons/emoji/unicode/270c.png",
    "vertical_traffic_light": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6a6.png",
    "vhs": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4fc.png",
    "vibration_mode": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f3.png",
    "video_camera": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4f9.png",
    "video_game": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3ae.png",
    "violin": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f3bb.png",
    "virgo": "https://assets-cdn.github.com/images/icons/emoji/unicode/264d.png",
    "volcano": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f30b.png",
    "vs": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f19a.png",
    "walking": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6b6.png",
    "waning_crescent_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f318.png",
    "waning_gibbous_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f316.png",
    "warning": "https://assets-cdn.github.com/images/icons/emoji/unicode/26a0.png",
    "watch": "https://assets-cdn.github.com/images/icons/emoji/unicode/231a.png",
    "water_buffalo": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f403.png",
    "watermelon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f349.png",
    "wave": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f44b.png",
    "wavy_dash": "https://assets-cdn.github.com/images/icons/emoji/unicode/3030.png",
    "waxing_crescent_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f312.png",
    "waxing_gibbous_moon": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f314.png",
    "wc": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6be.png",
    "weary": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f629.png",
    "wedding": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f492.png",
    "whale": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f433.png",
    "whale2": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f40b.png",
    "wheelchair": "https://assets-cdn.github.com/images/icons/emoji/unicode/267f.png",
    "white_check_mark": "https://assets-cdn.github.com/images/icons/emoji/unicode/2705.png",
    "white_circle": "https://assets-cdn.github.com/images/icons/emoji/unicode/26aa.png",
    "white_flower": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4ae.png",
    "white_large_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/2b1c.png",
    "white_medium_small_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/25fd.png",
    "white_medium_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/25fb.png",
    "white_small_square": "https://assets-cdn.github.com/images/icons/emoji/unicode/25ab.png",
    "white_square_button": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f533.png",
    "wind_chime": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f390.png",
    "wine_glass": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f377.png",
    "wink": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f609.png",
    "wolf": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f43a.png",
    "woman": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f469.png",
    "womans_clothes": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f45a.png",
    "womans_hat": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f452.png",
    "womens": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f6ba.png",
    "worried": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f61f.png",
    "wrench": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f527.png",
    "x": "https://assets-cdn.github.com/images/icons/emoji/unicode/274c.png",
    "yellow_heart": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f49b.png",
    "yen": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4b4.png",
    "yum": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f60b.png",
    "zap": "https://assets-cdn.github.com/images/icons/emoji/unicode/26a1.png",
    "zero": "https://assets-cdn.github.com/images/icons/emoji/unicode/0030-20e3.png",
    "zzz": "https://assets-cdn.github.com/images/icons/emoji/unicode/1f4a4.png"
}
# --end--


def get_github_emoji():  # pragma: no cover
    """Get Github's usable emoji."""

    try:
        resp = requests.get(
            'https://api.github.com/emojis',
            timeout=30
        )
    except Exception:
        return None

    return json.loads(resp.text)


def update_emoji():  # pragma: no cover
    """Update the emoji pattern in memory."""

    global RE_EMOJI
    global URL_EMOJI

    emoji_list = get_github_emoji()
    emoji_map = {}

    if emoji_list is not None:
        for emoji in emoji_list:
            url = emoji_list[emoji]
            m = RE_ASSET.match(url)
            if m:
                emoji_map[emoji] = m.group('image')

    if emoji_map:
        RE_EMOJI = ':(%s):' % '|'.join([re.escape(key) for key in sorted(emoji_map.keys())])
        URL_EMOJI = copy.copy(emoji_map)


class SimpleEmojiPattern(Pattern):
    """Return element of type `tag` with a text attribute of group(3) of a Pattern."""

    def __init__(self, pattern, css_class='emoji'):
        """Initialize."""

        self.css_class = css_class
        Pattern.__init__(self, pattern)

    def handleMatch(self, m):
        """Hanlde emoji pattern matches."""

        attributes = {
            "src": URL_EMOJI[m.group(2)],
            "alt": ":%s:" % m.group(2),
            "title": ":%s:" % m.group(2),
            "height": "20px",
            "width": "20px",
            "align": "absmiddle"
        }

        if self.css_class:
            attributes['class'] = self.css_class

        el = util.etree.Element("img", attributes)
        return el


class GithubEmojiExtension(Extension):
    """Add emoji extension to Markdown class."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            'css_class': [
                "emoji",
                "CSS class name to add to emoji images.  Use an empty string if you want no class"
                "- Default: 'emoji'"
            ],
            'offline': [
                True,
                "Uses the pre-built emoji list. Will not connect to the internet.  If 'False' "
                "githubemoji will pull down the latest list url format via github's API. "
                "Really only needed if the list is out of date and you must get the latest. "
                "- Default: True"
            ]
        }
        super(GithubEmojiExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """Add support for <del>test</del> tags as ~~test~~."""
        if not self.getConfigs()['offline'] and USE_REQUESTS:  # pragma: no cover
            update_emoji()
        css_class = self.getConfigs()["css_class"]
        md.inlinePatterns.add("github-emoji", SimpleEmojiPattern(RE_EMOJI, css_class), "<not_strong")


def makeExtension(*args, **kwargs):
    """Return extension."""

    return GithubEmojiExtension(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    # Update the emoji pattern in this file.

    import codecs
    import os

    file_name = os.path.abspath(__file__)

    def get_latest_emoji():
        """Get the latest emoji list."""

        # Update the file's regex pattern
        emoji_list = get_github_emoji()
        emoji_map = {}

        if emoji_list is not None:
            for emoji in emoji_list:
                url = emoji_list[emoji]
                m = RE_ASSET.match(url)
                if m:
                    emoji_map[emoji] = m.group('image')

        return emoji_map

    def update_emoji_source(file_name, emoji_map):
        """Update *this* source file with the latest emoji."""

        if emoji_map:
            replacement = None
            start = None
            end = None

            with codecs.open(file_name, 'r', encoding='utf-8') as f:
                m = re.match(r'(.*?# --start--\r?\n).*?(# --end--.*)', f.read(), re.DOTALL)
                if m:
                    start = m.group(1)
                    end = m.group(2)
                    replacement = 'RE_EMOJI = r\'\'\'(?x)\n:('
                    first = True
                    line = ''
                    for name in sorted(emoji_map.keys()):
                        escaped = re.escape(name)
                        if first:
                            first = False
                            sep = ''
                        else:
                            sep = '|'
                        if (len(line) + len(escaped) + len(sep)) > 110:
                            replacement += '\n    ' + line
                            line = ''
                        line += sep + escaped
                    replacement += '\n    ' + line + '\n):\'\'\'\n'
                    replacement += '\nURL_EMOJI = {'
                    first = True
                    for name in sorted(emoji_map.keys()):
                        if first:
                            first = False
                        else:
                            replacement += ','
                        replacement += '\n    "%s": "%s"' % (name, emoji_map[name])
                    replacement += '\n}\n'

            assert replacement is not None, "No emoji :("

            with codecs.open(file_name, 'w', encoding='utf-8') as f:
                f.write(start + replacement + end)

    try:
        emoji_map = get_latest_emoji()
        update_emoji_source(file_name, emoji_map)
        print('PASS - Emoji updated :)')
    except Exception as e:
        print(e)
        print('FAIL - No emoji :(')

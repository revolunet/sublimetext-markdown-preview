"""
mdownx.githubemoji
Really simple plugin to add support for
github emojis

MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from ..extensions import Extension
from ..inlinepatterns import Pattern
from .. import util

RE_EMOJI_PEOPLE = r''':(\+1|-1|alien|angel|anger|angry|anguished|astonished|baby|blue_heart|blush|boom|bow|bowtie|boy|bride_with_veil|broken_heart|bust_in_silhouette|busts_in_silhouette|clap|cold_sweat|collision|confounded|confused|construction_worker|cop|couple|couple_with_heart|couplekiss|cry|crying_cat_face|cupid|dancer|dancers|dash|disappointed|disappointed_relieved|dizzy|dizzy_face|droplet|ear|exclamation|expressionless|eyes|facepunch|family|fearful|feelsgood|feet|finnadie|fire|fist|flushed|frowning|fu|girl|goberserk|godmode|green_heart|grey_exclamation|grey_question|grimacing|grin|grinning|guardsman|haircut|hand|hankey|hear_no_evil|heart|heart_eyes|heart_eyes_cat|heartbeat|heartpulse|hurtrealbad|hushed|imp|information_desk_person|innocent|japanese_goblin|japanese_ogre|joy|joy_cat|kiss|kissing|kissing_cat|kissing_closed_eyes|kissing_heart|kissing_smiling_eyes|laughing|lips|love_letter|man|man_with_gua_pi_mao|man_with_turban|mask|massage|metal|muscle|musical_note|nail_care|neckbeard|neutral_face|no_good|no_mouth|nose|notes|ok_hand|ok_woman|older_man|older_woman|open_hands|open_mouth|pensive|persevere|person_frowning|person_with_blond_hair|person_with_pouting_face|point_down|point_left|point_right|point_up|point_up_2|poop|pouting_cat|pray|princess|punch|purple_heart|question|rage|rage1|rage2|rage3|rage4|raised_hand|raised_hands|raising_hand|relaxed|relieved|revolving_hearts|runner|running|satisfied|scream|scream_cat|see_no_evil|shit|skull|sleeping|sleepy|smile|smile_cat|smiley|smiley_cat|smiling_imp|smirk|smirk_cat|sob|sparkles|sparkling_heart|speak_no_evil|speech_balloon|star|star2|stuck_out_tongue|stuck_out_tongue_closed_eyes|stuck_out_tongue_winking_eye|sunglasses|suspect|sweat|sweat_drops|sweat_smile|thought_balloon|thumbsdown|thumbsup|tired_face|tongue|triumph|trollface|two_hearts|two_men_holding_hands|two_women_holding_hands|unamused|v|walking|wave|weary|wink|woman|worried|yellow_heart|yum|zzz):'''
RE_EMOJI_NATURE = r''':(ant|baby_chick|bear|bee|beetle|bird|blossom|blowfish|boar|bouquet|bug|cactus|camel|cat|cat2|cherry_blossom|chestnut|chicken|cloud|cow|cow2|crescent_moon|crocodile|cyclone|deciduous_tree|dog|dog2|dolphin|dragon|dragon_face|dromedary_camel|ear_of_rice|earth_africa|earth_americas|earth_asia|elephant|evergreen_tree|fallen_leaf|first_quarter_moon|first_quarter_moon_with_face|fish|foggy|four_leaf_clover|frog|full_moon|full_moon_with_face|globe_with_meridians|goat|hamster|hatched_chick|hatching_chick|herb|hibiscus|honeybee|horse|koala|last_quarter_moon|last_quarter_moon_with_face|leaves|leopard|maple_leaf|milky_way|monkey|monkey_face|moon|mouse|mouse2|mushroom|new_moon|new_moon_with_face|night_with_stars|ocean|octocat|octopus|ox|palm_tree|panda_face|partly_sunny|paw_prints|penguin|pig|pig2|pig_nose|poodle|rabbit|rabbit2|racehorse|ram|rat|rooster|rose|seedling|sheep|shell|snail|snake|snowflake|snowman|squirrel|sun_with_face|sunflower|sunny|tiger|tiger2|tropical_fish|tulip|turtle|umbrella|volcano|waning_crescent_moon|waning_gibbous_moon|water_buffalo|waxing_crescent_moon|waxing_gibbous_moon|whale|whale2|wolf|zap):'''
RE_EMOJI_OBJECTS = r''':(8ball|alarm_clock|apple|art|athletic_shoe|baby_bottle|balloon|bamboo|banana|bar_chart|baseball|basketball|bath|bathtub|battery|beer|beers|bell|bento|bicyclist|bikini|birthday|black_joker|black_nib|blue_book|bomb|book|bookmark|bookmark_tabs|books|boot|bowling|bread|briefcase|bulb|cake|calendar|calling|camera|candy|card_index|cd|chart_with_downwards_trend|chart_with_upwards_trend|cherries|chocolate_bar|christmas_tree|clapper|clipboard|closed_book|closed_lock_with_key|closed_umbrella|clubs|cocktail|coffee|computer|confetti_ball|cookie|corn|credit_card|crown|crystal_ball|curry|custard|dango|dart|date|diamonds|dollar|dolls|door|doughnut|dress|dvd|e-mail|egg|eggplant|electric_plug|email|envelope|envelope_with_arrow|euro|eyeglasses|fax|file_folder|fireworks|fish_cake|fishing_pole_and_fish|flags|flashlight|flipper|floppy_disk|flower_playing_cards|football|footprints|fork_and_knife|fried_shrimp|fries|game_die|gem|ghost|gift|gift_heart|golf|grapes|green_apple|green_book|guitar|gun|hamburger|hammer|handbag|headphones|hearts|high_brightness|high_heel|hocho|honey_pot|horse_racing|hourglass|hourglass_flowing_sand|ice_cream|icecream|inbox_tray|incoming_envelope|iphone|jack_o_lantern|jeans|key|kimono|lantern|ledger|lemon|lipstick|lock|lock_with_ink_pen|lollipop|loop|loud_sound|loudspeaker|low_brightness|mag|mag_right|mahjong|mailbox|mailbox_closed|mailbox_with_mail|mailbox_with_no_mail|mans_shoe|meat_on_bone|mega|melon|memo|microphone|microscope|minidisc|money_with_wings|moneybag|mortar_board|mountain_bicyclist|movie_camera|musical_keyboard|musical_score|mute|name_badge|necktie|newspaper|no_bell|notebook|notebook_with_decorative_cover|nut_and_bolt|oden|open_book|open_file_folder|orange_book|outbox_tray|package|page_facing_up|page_with_curl|pager|paperclip|peach|pear|pencil|pencil2|phone|pill|pineapple|pizza|postal_horn|postbox|pouch|poultry_leg|pound|purse|pushpin|radio|ramen|ribbon|rice|rice_ball|rice_cracker|rice_scene|ring|rugby_football|running_shirt_with_sash|sake|sandal|santa|satellite|saxophone|school_satchel|scissors|scroll|seat|shaved_ice|shirt|shoe|shower|ski|smoking|snowboarder|soccer|sound|space_invader|spades|spaghetti|sparkle|sparkler|speaker|stew|straight_ruler|strawberry|surfer|sushi|sweet_potato|swimmer|syringe|tada|tanabata_tree|tangerine|tea|telephone|telephone_receiver|telescope|tennis|toilet|tomato|tophat|triangular_ruler|trophy|tropical_drink|trumpet|tshirt|tv|unlock|vhs|video_camera|video_game|violin|watch|watermelon|wind_chime|wine_glass|womans_clothes|womans_hat|wrench|yen):'''
RE_EMOJI_PLACES = r''':(aerial_tramway|airplane|ambulance|anchor|articulated_lorry|atm|bank|barber|beginner|bike|blue_car|boat|bridge_at_night|bullettrain_front|bullettrain_side|bus|busstop|car|carousel_horse|checkered_flag|church|circus_tent|city_sunrise|city_sunset|cn|construction|convenience_store|crossed_flags|de|department_store|es|european_castle|european_post_office|factory|ferris_wheel|fire_engine|fountain|fr|fuelpump|gb|helicopter|hospital|hotel|hotsprings|house|house_with_garden|it|izakaya_lantern|japan|japanese_castle|jp|kr|light_rail|love_hotel|minibus|monorail|mount_fuji|mountain_cableway|mountain_railway|moyai|office|oncoming_automobile|oncoming_bus|oncoming_police_car|oncoming_taxi|performing_arts|police_car|post_office|railway_car|rainbow|red_car|rocket|roller_coaster|rotating_light|round_pushpin|rowboat|ru|sailboat|school|ship|slot_machine|speedboat|stars|station|statue_of_liberty|steam_locomotive|sunrise|sunrise_over_mountains|suspension_railway|taxi|tent|ticket|tokyo_tower|tractor|traffic_light|train|train2|tram|triangular_flag_on_post|trolleybus|truck|uk|us|vertical_traffic_light|warning|wedding):'''
RE_EMOJI_SYMBOLS = r''':(100|1234|a|ab|abc|abcd|accept|aquarius|aries|arrow_backward|arrow_double_down|arrow_double_up|arrow_down|arrow_down_small|arrow_forward|arrow_heading_down|arrow_heading_up|arrow_left|arrow_lower_left|arrow_lower_right|arrow_right|arrow_right_hook|arrow_up|arrow_up_down|arrow_up_small|arrow_upper_left|arrow_upper_right|arrows_clockwise|arrows_counterclockwise|b|baby_symbol|back|baggage_claim|ballot_box_with_check|bangbang|black_circle|black_large_square|black_medium_small_square|black_medium_square|black_small_square|black_square_button|cancer|capital_abcd|capricorn|chart|children_crossing|cinema|cl|clock1|clock10|clock1030|clock11|clock1130|clock12|clock1230|clock130|clock2|clock230|clock3|clock330|clock4|clock430|clock5|clock530|clock6|clock630|clock7|clock730|clock8|clock830|clock9|clock930|congratulations|cool|copyright|curly_loop|currency_exchange|customs|diamond_shape_with_a_dot_inside|do_not_litter|eight|eight_pointed_black_star|eight_spoked_asterisk|end|fast_forward|five|four|free|gemini|hash|heart_decoration|heavy_check_mark|heavy_division_sign|heavy_dollar_sign|heavy_exclamation_mark|heavy_minus_sign|heavy_multiplication_x|heavy_plus_sign|id|ideograph_advantage|information_source|interrobang|keycap_ten|koko|large_blue_circle|large_blue_diamond|large_orange_diamond|left_luggage|left_right_arrow|leftwards_arrow_with_hook|leo|libra|link|m|mens|metro|mobile_phone_off|negative_squared_cross_mark|new|ng|nine|no_bicycles|no_entry|no_entry_sign|no_mobile_phones|no_pedestrians|no_smoking|non-potable_water|o|o2|ok|on|one|ophiuchus|parking|part_alternation_mark|passport_control|pisces|potable_water|put_litter_in_its_place|radio_button|recycle|red_circle|registered|repeat|repeat_one|restroom|rewind|sa|sagittarius|scorpius|secret|seven|shipit|signal_strength|six|six_pointed_star|small_blue_diamond|small_orange_diamond|small_red_triangle|small_red_triangle_down|soon|sos|symbols|taurus|three|tm|top|trident|twisted_rightwards_arrows|two|u5272|u5408|u55b6|u6307|u6708|u6709|u6e80|u7121|u7533|u7981|u7a7a|underage|up|vibration_mode|virgo|vs|wavy_dash|wc|wheelchair|white_check_mark|white_circle|white_flower|white_large_square|white_medium_small_square|white_medium_square|white_small_square|white_square_button|womens|x|zero):'''

GITHUB_ASSETS = "https://assets-cdn.github.com/images/icons/emoji/%s.png"


class SimpleEmojiPattern(Pattern):
    """
    Return element of type `tag` with a text attribute of group(3)
    of a Pattern.

    """
    def __init__(self, pattern):
        Pattern.__init__(self, pattern)

    def handleMatch(self, m):
        el = util.etree.Element(
            "img",
            {
                "src": GITHUB_ASSETS % m.group(2),
                "alt": m.group(2),
                "title": m.group(2),
                "height": "20px",
                "width": "20px",
                "align": "absmiddle"
            }
        )
        return el


class GithubEmojiExtension(Extension):
    """Adds delete extension to Markdown class."""

    def extendMarkdown(self, md, md_globals):
        """Add support for <del>test</del> tags as ~~test~~"""

        md.inlinePatterns.add("github_emoji_people", SimpleEmojiPattern(RE_EMOJI_PEOPLE), "<not_strong")
        md.inlinePatterns.add("github_emoji_nature", SimpleEmojiPattern(RE_EMOJI_NATURE), "<not_strong")
        md.inlinePatterns.add("github_emoji_objects", SimpleEmojiPattern(RE_EMOJI_OBJECTS), "<not_strong")
        md.inlinePatterns.add("github_emoji_places", SimpleEmojiPattern(RE_EMOJI_PLACES), "<not_strong")
        md.inlinePatterns.add("github_emoji_symbols", SimpleEmojiPattern(RE_EMOJI_SYMBOLS), "<not_strong")


def makeExtension(configs={}):
    return GithubEmojiExtension(configs=dict(configs))

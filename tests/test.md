---
    # Builtin values
    references:
        - references.md
        - abbreviations.md
        - footnotes.md

    destination: destination.html

    # Meta Data
    title: Test Page
    author:
        - John Doe
        - Jane Doe

    # Settings overrides
    settings:
        enabled_extensions:
        - extra
        - github
        - insert
        - progressbar
        - toc
        - headerid
        - smarty
        - meta
        - wikilinks
        - admonition
        - admonitionicon
        - codehilite(guess_lang=False,pygments_style=github)
---
test: This tests the meta extension
title: This title will be overridden by YAML

!!! hint "Recommended Extentions for Testing"
    This is mainly used to test the Python Markdown parser.

    - extra
    - github
    - insert
    - toc
    - headerid
    - smarty
    - meta
    - wikilinks
    - footnotes
    - admonition
    - admonitionicon
    - codehilite(guess_lang=False,pygments_style=github)

    !!! Caution "Testing Note"
        - `sane_lists` will alter the results of the second test in [Mixed Lists](#mixed-lists). When turned off, this test will have all list items mixed and aligned proper.  With `sane_lists` on, some will not be recognized, and some items may be aligned in different lists.
        - having `guess_lang=False` allows the testing of the selective highlighting.  When omitted or set `true`, it can be expected that all of the blocks will be highlighted to some extent.
        - Most tests are spot checked at this point or a link can be clicked to verify it is working.
        - base64, absolute paths, and external resources require this to be in an unzipped sublime package environment.


# Cheat Sheet and Test
[TOC]

## Headers

```
# H1
## H2
### H3
#### H4
##### H5
###### H6
### Duplicate Header
### Duplicate Header
```

# H1
## H2
### H3
#### H4
##### H5
###### H6
### Duplicate Header
### Duplicate Header

## Paragraphs
```
This is a paragraph.
I am still part of the paragraph.

New paragraph.
```

This is a paragraph.
I am still part of the paragraph.

New paragraph.

## Inline

```
`inline block`

**bold 1** and __bold 2__

*italic 1*  and _italic 2_

~~strike~~


***bold 1 and italic 1***

___bold 2 and italic 2___

__*bold 2 and italic 1*__

**_bold 1 and italic 2_**


~~*strike italic 1*~~ and *~~strike italic 2~~*

~~_strike italic 2_~~ and  _~~strike italic 2~~_


~~**strike bold 1**~~ and **~~strike bold 1~~**

~~__strike bold 2__~~ and __~~strike bold 2~~__


~~***strike italic 1 bold 1***~~ and ***~~strike italic 1 bold 1~~***

~~___strike italic 2 bold 2___~~ and ___~~strike italic 2 bold 2~~___

**~~*strike italic 1 bold 1*~~** and *~~**strike italic 1 bold 1**~~*

__~~_strike italic 2 bold 2_~~__ and _~~__strike italic 2 bold 2__~~_

**~~_strike italic 2 bold 1_~~** and _~~**strike italic 2 bold 1**~~_

__~~*strike italic 1 bold 2*~~__ and *~~__strike italic 1 bold 2__~~*

```

`inline block`

**bold 1** and __bold 2__

*italic 1*  and _italic 2_

~~strike~~


***bold 1 and italic 1***

___bold 2 and italic 2___

__*bold 2 and italic 1*__

**_bold 1 and italic 2_**


~~*strike italic 1*~~ and *~~strike italic 2~~*

~~_strike italic 2_~~ and  _~~strike italic 2~~_


~~**strike bold 1**~~ and **~~strike bold 1~~**

~~__strike bold 2__~~ and __~~strike bold 2~~__


~~***strike italic 1 bold 1***~~ and ***~~strike italic 1 bold 1~~***

~~___strike italic 2 bold 2___~~ and ___~~strike italic 2 bold 2~~___

**~~*strike italic 1 bold 1*~~** and *~~**strike italic 1 bold 1**~~*

__~~_strike italic 2 bold 2_~~__ and _~~__strike italic 2 bold 2__~~_

**~~_strike italic 2 bold 1_~~** and _~~**strike italic 2 bold 1**~~_

__~~*strike italic 1 bold 2*~~__ and *~~__strike italic 1 bold 2__~~*


## Links
Footnote, reference sources are provided in separate markdowns files specified in frontmatter.
```
[Reference Link][1]

Footnotes[^1] have a label[^label] and a definition[^!DEF]

Web image
![Web Picture](http://www.revolunet.com/static/parisjs8/img/logo-revolunet-carre.jpg "Web Picture")

Local image
![Local Picture](logo-revolunet-carre.jpg "Local Picture")

contact@revolunet.com

https://github.com/revolunet/sublimetext-markdown-preview/

This is a link https://github.com/revolunet/sublimetext-markdown-preview/.

This is a link "https://github.com/revolunet/sublimetext-markdown-preview/".

With this link (https://github.com/revolunet/sublimetext-markdown-preview/), it still works.

    [1]: https://github.com/revolunet/sublimetext-markdown-preview/
    [^1]: This is a footnote
    [^label]: A footnote on "label"
    [^!DEF]: The footnote for definition
```

[Reference Link][1]

Footnotes[^1] have a label[^label] and a definition[^!DEF]

Web image
![Web Picture](http://www.revolunet.com/static/parisjs8/img/logo-revolunet-carre.jpg "Web Picture")

Local image
![Local Picture](logo-revolunet-carre.jpg "Local Picture")

www.google.com

contact@revolunet.com

https://github.com/revolunet/sublimetext-markdown-preview/

This is a link https://github.com/revolunet/sublimetext-markdown-preview/.

This is a link "https://github.com/revolunet/sublimetext-markdown-preview/".

With this link (https://github.com/revolunet/sublimetext-markdown-preview/), it still works.

## Abbreviation
Abreviations source are found in a separate markdown file specified in frontmatter.
```
The HTML specification 
is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]:  World Wide Web Consortium
```

The HTML specification 
is maintained by the W3C.

## Unordered List

```
Unordered List

- item 1
    * item A
    * item B
        more text
        + item a
        + item b
        + item c
    * item C
- item 2
- item 3
```

Unordered List

- item 1
    * item A
    * item B
        more text
        + item a
        + item b
        + item c
    * item C
- item 2
- item 3


## Ordered List
```
Ordered List

1. item 1
    1. item A
    2. item B
        more text
        1. item a
        2. item b
        3. item c
    3. item C
2. item 2
3. item 3
```

Ordered List

1. item 1
    1. item A
    2. item B
        more text
        1. item a
        2. item b
        3. item c
    3. item C
2. item 2
3. item 3

## Task List
```
Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a
        + [ ] item b
        + [x] item c
    * [X] item C
- [ ] item 2
- [ ] item 3
```

Task List

- [X] item 1
    * [X] item A
    * [ ] item B
        more text
        + [x] item a
        + [ ] item b
        + [x] item c
    * [X] item C
- [ ] item 2
- [ ] item 3

## Mixed Lists
`Really Mixed Lists` should break with `sane_lists` on.

```
Mixed Lists

- item 1
    * [X] item A
    * [ ] item B
        more text
        1. item a
        2. itemb
        3. item c
    * [X] item C
- item 2
- item 3


Really Mixed Lists

- item 1
    * [X] item A
    - item B
        more text
        1. item a
        + itemb
        + [ ] item c
    3. item C
2. item 2
- [X] item 3
```

Mixed Lists

- item 1
    * [X] item A
    * [ ] item B
        more text
        1. item a
        2. itemb
        3. item c
    * [X] item C
- item 2
- item 3


Really Mixed Lists

- item 1
    * [X] item A
    - item B
        more text
        1. item a
        + itemb
        + [ ] item c
    3. item C
2. item 2
- [X] item 3


## Dictionary
```
Dictionary
:   item 1

    item 2

    item 3
```

Dictionary
:   item 1

    item 2

    item 3

## Blocks
```
    This is a block.
    
    This is more of a block.

```

    This is a block.
    
    This is more of a block.


## Block Quotes
```
> This is a block quote
>> How does it look?
```

> This is a block quote.
>> How does it look?
> I think it looks good.

## Fenced Block
Assuming guessing is not enabled.

`````
```
// Fenced **without** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

```javascript
// Fenced **with** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```
`````

```
// Fenced **without** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

```javascript
// Fenced **with** highlighting
function doIt() {
    for (var i = 1; i <= slen ; i^^) {
        setTimeout("document.z.textdisplay.value = newMake()", i*300);
        setTimeout("window.status = newMake()", i*300);
    }
}
```

## Tables

```
| _Colors_      | Fruits          | Vegetable         |
| ------------- |:---------------:| -----------------:|
| Red           | *Apple*         | [Pepper](#Tables) |
| ~~Orange~~    | Oranges         | **Carrot**        |
| Green         | ~~***Pears***~~ | Spinach           |
```

| _Colors_      | Fruits          | Vegetable    |
| ------------- |:---------------:| ------------:|
| Red           | *Apple*         | Pepper       |
| ~~Orange~~    | Oranges         | **Carrot**   |
| Green         | ~~***Pears***~~ | Spinach      |

## Smart Strong
```
Text with double__underscore__words.

__Strong__ still works.

__this__works__too__
```

Text with double__underscore__words.

__Strong__ still works.

__this__works__too__

## Smarty
```
"double quotes"

'single quotes'

da--sh

elipsis...
```

"double quotes"

'single quotes'

da--sh

elipsis...

## Attribute List
```
Normal Text

Modified Text
{: style="font-weight:bold;" }
```

Normal Text

Modified Text
{: style="font-weight:bold;" }

## Admonition
```
!!! Attention "Success!"
    You can use inline ~~stuff~~ markup too!

!!! Hint "Info!"
    - Here is some info.
    - And some more

!!! Caution "Warning!"
    - [X] Make sure you turn off the stove
    - [X] Don't run with scissors

!!! Danger "Alert!"
    You really need to read [this](#admonition)!

!!! Question "Question?"
    Are you serious?

!!! Note "Note"
    :smile:

    > Not all markup can be placed in these boxes, but you can fit all sorts of things in them. But you will notice that the styles don't always play nice with each other.  Additional CSS could fix this though.

    Stuff like _this_ works too.

    | _Colors_      | Fruits          | Vegetable    |
    | ------------- |:---------------:| ------------:|
    | Red           | *Apple*         | Pepper       |
    | ~~Orange~~    | Oranges         | **Carrot**   |
    | Green         | ~~***Pears***~~ | Spinach      |

!!! Unknown "Title"
    Default class style
```

!!! Attention "Success!"
    You can use inline ~~stuff~~ markup too!

!!! Hint "Info!"
    - Here is some info.
    - And some more

!!! Caution "Warning!"
    - [X] Make sure you turn off the stove
    - [X] Don't run with scissors

!!! Danger "Alert!"
    You really need to read [this](#admonition)!

!!! Question "Question?"
    Are you serious?

!!! Note "Note"
    :smile:

    > Not all markup can be placed in these boxes, but you can fit all sorts of things in them. But you will notice that the styles don't always play nice with each other.  Additional CSS could fix this though.

    Stuff like _this_ works too.

    | _Colors_      | Fruits          | Vegetable    |
    | ------------- |:---------------:| ------------:|
    | Red           | *Apple*         | Pepper       |
    | ~~Orange~~    | Oranges         | **Carrot**   |
    | Green         | ~~***Pears***~~ | Spinach      |

!!! Unknown "Title"
    Default class style

## Github Emoji
```
This is a test for emoji :smile:.  The emojis are images linked to github assets :octocat:.
```

This is a test for emoji :smile:.  The emojis are images linked to github assets :octocat:.

### People

:+1::-1::alien::angel::anger::angry::anguished::astonished::baby::blue_heart::blush::boom::bow::bowtie::boy::bride_with_veil::broken_heart::bust_in_silhouette::busts_in_silhouette::clap::cold_sweat::collision::confounded::confused::construction_worker::cop::couple::couple_with_heart::couplekiss::cry::crying_cat_face::cupid::dancer::dancers::dash::disappointed::disappointed_relieved::dizzy::dizzy_face::droplet::ear::exclamation::expressionless::eyes::facepunch::family::fearful::feelsgood::feet::finnadie::fire::fist::flushed::frowning::fu::girl::goberserk::godmode::green_heart::grey_exclamation::grey_question::grimacing::grin::grinning::guardsman::haircut::hand::hankey::hear_no_evil::heart::heart_eyes::heart_eyes_cat::heartbeat::heartpulse::hurtrealbad::hushed::imp::information_desk_person::innocent::japanese_goblin::japanese_ogre::joy::joy_cat::kiss::kissing::kissing_cat::kissing_closed_eyes::kissing_heart::kissing_smiling_eyes::laughing::lips::love_letter::man::man_with_gua_pi_mao::man_with_turban::mask::massage::metal::muscle::musical_note::nail_care::neckbeard::neutral_face::no_good::no_mouth::nose::notes::ok_hand::ok_woman::older_man::older_woman::open_hands::open_mouth::pensive::persevere::person_frowning::person_with_blond_hair::person_with_pouting_face::point_down::point_left::point_right::point_up::point_up_2::poop::pouting_cat::pray::princess::punch::purple_heart::question::rage::rage1::rage2::rage3::rage4::raised_hand::raised_hands::raising_hand::relaxed::relieved::revolving_hearts::runner::running::satisfied::scream::scream_cat::see_no_evil::shit::skull::sleeping::sleepy::smile::smile_cat::smiley::smiley_cat::smiling_imp::smirk::smirk_cat::sob::sparkles::sparkling_heart::speak_no_evil::speech_balloon::star::star2::stuck_out_tongue::stuck_out_tongue_closed_eyes::stuck_out_tongue_winking_eye::sunglasses::suspect::sweat::sweat_drops::sweat_smile::thought_balloon::thumbsdown::thumbsup::tired_face::tongue::triumph::trollface::two_hearts::two_men_holding_hands::two_women_holding_hands::unamused::v::walking::wave::weary::wink::woman::worried::yellow_heart::yum::zzz:

### Nature

:ant::baby_chick::bear::bee::beetle::bird::blossom::blowfish::boar::bouquet::bug::cactus::camel::cat::cat2::cherry_blossom::chestnut::chicken::cloud::cow::cow2::crescent_moon::crocodile::cyclone::deciduous_tree::dog::dog2::dolphin::dragon::dragon_face::dromedary_camel::ear_of_rice::earth_africa::earth_americas::earth_asia::elephant::evergreen_tree::fallen_leaf::first_quarter_moon::first_quarter_moon_with_face::fish::foggy::four_leaf_clover::frog::full_moon::full_moon_with_face::globe_with_meridians::goat::hamster::hatched_chick::hatching_chick::herb::hibiscus::honeybee::horse::koala::last_quarter_moon::last_quarter_moon_with_face::leaves::leopard::maple_leaf::milky_way::monkey::monkey_face::moon::mouse::mouse2::mushroom::new_moon::new_moon_with_face::night_with_stars::ocean::octocat::octopus::ox::palm_tree::panda_face::partly_sunny::paw_prints::penguin::pig::pig2::pig_nose::poodle::rabbit::rabbit2::racehorse::ram::rat::rooster::rose::seedling::sheep::shell::snail::snake::snowflake::snowman::squirrel::sun_with_face::sunflower::sunny::tiger::tiger2::tropical_fish::tulip::turtle::umbrella::volcano::waning_crescent_moon::waning_gibbous_moon::water_buffalo::waxing_crescent_moon::waxing_gibbous_moon::whale::whale2::wolf::zap:

### Objects

:8ball::alarm_clock::apple::art::athletic_shoe::baby_bottle::balloon::bamboo::banana::bar_chart::baseball::basketball::bath::bathtub::battery::beer::beers::bell::bento::bicyclist::bikini::birthday::black_joker::black_nib::blue_book::bomb::book::bookmark::bookmark_tabs::books::boot::bowling::bread::briefcase::bulb::cake::calendar::calling::camera::candy::card_index::cd::chart_with_downwards_trend::chart_with_upwards_trend::cherries::chocolate_bar::christmas_tree::clapper::clipboard::closed_book::closed_lock_with_key::closed_umbrella::clubs::cocktail::coffee::computer::confetti_ball::cookie::corn::credit_card::crown::crystal_ball::curry::custard::dango::dart::date::diamonds::dollar::dolls::door::doughnut::dress::dvd::e-mail::egg::eggplant::electric_plug::email::envelope::envelope_with_arrow::euro::eyeglasses::fax::file_folder::fireworks::fish_cake::fishing_pole_and_fish::flags::flashlight::flipper::floppy_disk::flower_playing_cards::football::footprints::fork_and_knife::fried_shrimp::fries::game_die::gem::ghost::gift::gift_heart::golf::grapes::green_apple::green_book::guitar::gun::hamburger::hammer::handbag::headphones::hearts::high_brightness::high_heel::hocho::honey_pot::horse_racing::hourglass::hourglass_flowing_sand::ice_cream::icecream::inbox_tray::incoming_envelope::iphone::jack_o_lantern::jeans::key::kimono::lantern::ledger::lemon::lipstick::lock::lock_with_ink_pen::lollipop::loop::loud_sound::loudspeaker::low_brightness::mag::mag_right::mahjong::mailbox::mailbox_closed::mailbox_with_mail::mailbox_with_no_mail::mans_shoe::meat_on_bone::mega::melon::memo::microphone::microscope::minidisc::money_with_wings::moneybag::mortar_board::mountain_bicyclist::movie_camera::musical_keyboard::musical_score::mute::name_badge::necktie::newspaper::no_bell::notebook::notebook_with_decorative_cover::nut_and_bolt::oden::open_book::open_file_folder::orange_book::outbox_tray::package::page_facing_up::page_with_curl::pager::paperclip::peach::pear::pencil::pencil2::phone::pill::pineapple::pizza::postal_horn::postbox::pouch::poultry_leg::pound::purse::pushpin::radio::ramen::ribbon::rice::rice_ball::rice_cracker::rice_scene::ring::rugby_football::running_shirt_with_sash::sake::sandal::santa::satellite::saxophone::school_satchel::scissors::scroll::seat::shaved_ice::shirt::shoe::shower::ski::smoking::snowboarder::soccer::sound::space_invader::spades::spaghetti::sparkle::sparkler::speaker::stew::straight_ruler::strawberry::surfer::sushi::sweet_potato::swimmer::syringe::tada::tanabata_tree::tangerine::tea::telephone::telephone_receiver::telescope::tennis::toilet::tomato::tophat::triangular_ruler::trophy::tropical_drink::trumpet::tshirt::tv::unlock::vhs::video_camera::video_game::violin::watch::watermelon::wind_chime::wine_glass::womans_clothes::womans_hat::wrench::yen:

### Places

:aerial_tramway::airplane::ambulance::anchor::articulated_lorry::atm::bank::barber::beginner::bike::blue_car::boat::bridge_at_night::bullettrain_front::bullettrain_side::bus::busstop::car::carousel_horse::checkered_flag::church::circus_tent::city_sunrise::city_sunset::cn::construction::convenience_store::crossed_flags::de::department_store::es::european_castle::european_post_office::factory::ferris_wheel::fire_engine::fountain::fr::fuelpump::gb::helicopter::hospital::hotel::hotsprings::house::house_with_garden::it::izakaya_lantern::japan::japanese_castle::jp::kr::light_rail::love_hotel::minibus::monorail::mount_fuji::mountain_cableway::mountain_railway::moyai::office::oncoming_automobile::oncoming_bus::oncoming_police_car::oncoming_taxi::performing_arts::police_car::post_office::railway_car::rainbow::red_car::rocket::roller_coaster::rotating_light::round_pushpin::rowboat::ru::sailboat::school::ship::slot_machine::speedboat::stars::station::statue_of_liberty::steam_locomotive::sunrise::sunrise_over_mountains::suspension_railway::taxi::tent::ticket::tokyo_tower::tractor::traffic_light::train::train2::tram::triangular_flag_on_post::trolleybus::truck::uk::us::vertical_traffic_light::warning::wedding:

### Symbols

:100::1234::a::ab::abc::abcd::accept::aquarius::aries::arrow_backward::arrow_double_down::arrow_double_up::arrow_down::arrow_down_small::arrow_forward::arrow_heading_down::arrow_heading_up::arrow_left::arrow_lower_left::arrow_lower_right::arrow_right::arrow_right_hook::arrow_up::arrow_up_down::arrow_up_small::arrow_upper_left::arrow_upper_right::arrows_clockwise::arrows_counterclockwise::b::baby_symbol::back::baggage_claim::ballot_box_with_check::bangbang::black_circle::black_large_square::black_medium_small_square::black_medium_square::black_small_square::black_square_button::cancer::capital_abcd::capricorn::chart::children_crossing::cinema::cl::clock1::clock10::clock1030::clock11::clock1130::clock12::clock1230::clock130::clock2::clock230::clock3::clock330::clock4::clock430::clock5::clock530::clock6::clock630::clock7::clock730::clock8::clock830::clock9::clock930::congratulations::cool::copyright::curly_loop::currency_exchange::customs::diamond_shape_with_a_dot_inside::do_not_litter::eight::eight_pointed_black_star::eight_spoked_asterisk::end::fast_forward::five::four::free::gemini::hash::heart_decoration::heavy_check_mark::heavy_division_sign::heavy_dollar_sign::heavy_exclamation_mark::heavy_minus_sign::heavy_multiplication_x::heavy_plus_sign::id::ideograph_advantage::information_source::interrobang::keycap_ten::koko::large_blue_circle::large_blue_diamond::large_orange_diamond::left_luggage::left_right_arrow::leftwards_arrow_with_hook::leo::libra::link::m::mens::metro::mobile_phone_off::negative_squared_cross_mark::new::ng::nine::no_bicycles::no_entry::no_entry_sign::no_mobile_phones::no_pedestrians::no_smoking::non-potable_water::o::o2::ok::on::one::ophiuchus::parking::part_alternation_mark::passport_control::pisces::potable_water::put_litter_in_its_place::radio_button::recycle::red_circle::registered::repeat::repeat_one::restroom::rewind::sa::sagittarius::scorpius::secret::seven::shipit::signal_strength::six::six_pointed_star::small_blue_diamond::small_orange_diamond::small_red_triangle::small_red_triangle_down::soon::sos::symbols::taurus::three::tm::top::trident::twisted_rightwards_arrows::two::u5272::u5408::u55b6::u6307::u6708::u6709::u6e80::u7121::u7533::u7981::u7a7a::underage::up::vibration_mode::virgo::vs::wavy_dash::wc::wheelchair::white_check_mark::white_circle::white_flower::white_large_square::white_medium_small_square::white_medium_square::white_small_square::white_square_button::womens::x::zero:

## Insert
```
^^insert^^

^^*insert italic*^^  *^^insert italic 2^^*

^^_insert italic_^^  _^^insert italic 2^^_

^^**insert bold**^^  **^^insert bold 2^^**

^^__insert bold__^^  __^^insert bold 2^^__

^^***insert italic bold***^^  ***^^insert italic bold 2^^***

^^___insert italic bold___^^  ___^^insert italic bold 2^^___

**^^*insert italic bold*^^**  *^^**insert italic bold 2**^^*

__^^_insert italic bold_^^__  _^^__insert italic bold 2__^^_

**^^_insert italic bold_^^**  _^^**insert italic bold 2**^^_

__^^*insert italic bold*^^__  *^^__insert italic bold 2__^^*
```

^^insert^^

^^*insert italic*^^  *^^insert italic 2^^*

^^_insert italic_^^  _^^insert italic 2^^_

^^**insert bold**^^  **^^insert bold 2^^**

^^__insert bold__^^  __^^insert bold 2^^__

^^***insert italic bold***^^  ***^^insert italic bold 2^^***

^^___insert italic bold___^^  ___^^insert italic bold 2^^___

**^^*insert italic bold*^^**  *^^**insert italic bold 2**^^*

__^^_insert italic bold_^^__  _^^__insert italic bold 2__^^_

**^^_insert italic bold_^^**  _^^**insert italic bold 2**^^_

__^^*insert italic bold*^^__  *^^__insert italic bold 2__^^*

# Progress
Progress bars are block elements and it is recommened to put a newline before and after.  But they will be recognized inline, but they will be on their own line.

Normally you would just globally set your additional classes: `progressbar(addclasses=candystripe-animate)`, but here we want to test the inline class adding and inline control of level classes.

To turn off level classes (which are used to decide special colors for certain percentages) you could just use `progressbar(levelclass=False)`.
```
| Test                      | Result                                          |
|---------------------------|-------------------------------------------------|
|Animated Color Levels: 0%  |[==0% "0%"]{addclasses="candystripe-animate"}    |
|Animated Color Levels: 5%  |[==5% "5%"]{addclasses="candystripe-animate"}    |
|Animated Color Levels: 25% |[==25% "25%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 45% |[==45% "45%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 65% |[==65% "65%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 85% |[==85% "85%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 100%|[==100% "100%"]{addclasses="candystripe-animate"}|
|Division Percentage        |[== 212.2/537 "212.2/537 Testing division"]      |
|No Label                   |[== 50%]                                         |
|Inline                     |Before[== 50% I'm a block!]After                 |
|No Levels and Gloss        |[== 50%]{levelclass="false" addclasses="gloss"}  |
```

| Test                      | Result                                          |
|---------------------------|-------------------------------------------------|
|Animated Color Levels: 0%  |[==0% "0%"]{addclasses="candystripe-animate"}    |
|Animated Color Levels: 5%  |[==5% "5%"]{addclasses="candystripe-animate"}    |
|Animated Color Levels: 25% |[==25% "25%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 45% |[==45% "45%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 65% |[==65% "65%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 85% |[==85% "85%"]{addclasses="candystripe-animate"}  |
|Animated Color Levels: 100%|[==100% "100%"]{addclasses="candystripe-animate"}|
|Division Percentage        |[== 212.2/537 "212.2/537 Testing division"]      |
|No Label                   |[== 50%]                                         |
|Inline                     |Before[== 50% I'm a block!]After                 |
|No Levels and Gloss        |[== 50%]{levelclass="false" addclasses="gloss"}  |

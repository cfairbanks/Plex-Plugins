import re

ECW_HARDCORE_TV_TVRAGE = '1598'
ECW_HARDCORE_TV_TVDB = '76781'
ECW_ON_SCIFI_TVRAGE = '12105'
ECW_ON_SCIFI_TVDB = '79859'
ECW_ON_TNN_TVRAGE = '1597'
ECW_ON_TNN_TVDB = '76780'
ECW_PPV_TVRAGE = '1413'
ECW_PPV_TVDB = '73512'

ROH_WRESTLING_TVRAGE = '29472'
ROH_WRESTLING_TVDB = '266806'

TNA_IMPACT_TVRAGE = '6368'
TNA_IMPACT_TVDB = '264684'
TNA_PPV_TVRAGE = '548'
TNA_PPV_TVDB = None

WCW_NITRO_TVRAGE = '6547'
WCW_NITRO_TVDB = '76962'
WCW_THUNDER_TVRAGE = '6550'
WCW_THUNDER_TVDB = '76782'
WCW_WORLDWIDE_TVRAGE = '685'
WCW_WORLDWIDE_TVDB = '71091'
WCW_PPV_TVRAGE = '6548'
WCW_PPV_TVDB = '276391'

WWE_HEAT_TVRAGE = '5392'
WWE_HEAT_TVDB = '72174'
WWE_NXT_TVRAGE = '25100'
WWE_NXT_TVDB = '144541'
WWE_PPV_TVRAGE = '6652'
WWE_PPV_TVDB = '70353'
WWE_RAW_TVRAGE = '6659'
WWE_RAW_TVDB = '76779'
WWE_SHOTGUN_TVRAGE = '6661'
WWE_SHOTGUN_TVDB = None
WWE_SMACKDOWN_TVRAGE = '6655'
WWE_SMACKDOWN_TVDB = '75640'
WWE_TOTAL_DIVAS_TVRAGE = '35554'
WWE_TOTAL_DIVAS_TVDB = '271525'
WWE_TOUGH_ENOUGH_TVRAGE = '6656'
WWE_TOUGH_ENOUGH_TVDB = '76775'

TVDB_DICTIONARY = {
    ECW_HARDCORE_TV_TVRAGE: ECW_HARDCORE_TV_TVDB,
    ECW_ON_SCIFI_TVRAGE: ECW_ON_SCIFI_TVDB,
    ECW_ON_TNN_TVRAGE: ECW_ON_TNN_TVDB,
    ECW_PPV_TVRAGE: ECW_PPV_TVDB,

    ROH_WRESTLING_TVRAGE: ROH_WRESTLING_TVDB,

    TNA_IMPACT_TVRAGE: TNA_IMPACT_TVDB,
    TNA_PPV_TVRAGE: TNA_PPV_TVDB,

    WCW_NITRO_TVRAGE: WCW_NITRO_TVDB,
    WCW_THUNDER_TVRAGE: WCW_THUNDER_TVDB,
    WCW_WORLDWIDE_TVRAGE: WCW_WORLDWIDE_TVDB,
    WCW_PPV_TVRAGE: WCW_PPV_TVDB,

    WWE_HEAT_TVRAGE: WWE_HEAT_TVDB,
    WWE_NXT_TVRAGE: WWE_NXT_TVDB,
    WWE_PPV_TVRAGE: WWE_PPV_TVDB,
    WWE_RAW_TVRAGE: WWE_RAW_TVDB,
    WWE_SHOTGUN_TVRAGE: WWE_SHOTGUN_TVDB,
    WWE_SMACKDOWN_TVRAGE: WWE_SMACKDOWN_TVDB,
    WWE_TOTAL_DIVAS_TVRAGE: WWE_TOTAL_DIVAS_TVDB,
    WWE_TOUGH_ENOUGH_TVRAGE: WWE_TOUGH_ENOUGH_TVDB,
}

VARIATIONS_LIST = [
    ['ECW', 'Extreme Championship Wrestling'],
    ['TNA', 'Total Non-stop Action'],
    ['ROH', 'Ring Of Honor'],
    [
        'Smackdown',
        'Smackdown!',
        'Friday Night Smackdown',
        'Friday Night Smackdown!',
    ],
    ['WCW', 'World Championship Wrestling'],
    ['WWE', 'World Wrestling Entertainment', 'WWF', 'World Wrestling Federation'],
]


def convert_tvrage_to_tvdb(tvrage_id):
    if tvrage_id in TVDB_DICTIONARY:
        return TVDB_DICTIONARY[tvrage_id]
    else:
        return None


def get_show_name_variations(show_name, ignore_case=True):
    show_name_variations = [show_name]

    patterns = {
        "^%s\s+": "%s ",
        "\s+%s\s+": " %s ",
        "\s+%s$": " %s",
    }

    for variation_list in VARIATIONS_LIST:
        for search_variation in variation_list:
            for replacement_variation in variation_list:
                for search_pattern, replacement_pattern in patterns.iteritems():
                    if ignore_case:
                        search_regexp = re.compile(search_pattern % search_variation, re.IGNORECASE)
                    else:
                        search_regexp = re.compile(search_pattern % search_variation)

                    sub = search_regexp.sub(replacement_pattern % replacement_variation, show_name)
                    if sub not in variation_list:
                        show_name_variations.append(sub)

    return show_name_variations
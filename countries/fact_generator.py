"""
Knowledge Base Generator
Generates a Prolog-style .pl fact file from Python data classes.
Both facts AND rules are defined as data, then rendered automatically.
"""

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Data classes — Facts
# ---------------------------------------------------------------------------


@dataclass
class Country:
    name: str  # e.g. "spain"
    region: str  # e.g. "europe"
    currency: str  # e.g. "euro"
    languages: list[str]  # e.g. ["spanish"]
    capital: str  # e.g. "madrid"
    cities: list[str] = field(default_factory=list)  # non-capital cities
    borders: list[str] = field(default_factory=list)  # neighbouring country names
    memberships: list[str] = field(default_factory=list)  # org names


# ---------------------------------------------------------------------------
# Data classes — Rules
# ---------------------------------------------------------------------------


@dataclass
class Rule:
    """
    One Prolog rule:  head :- body_clause_1, body_clause_2, ...

    head_functor : str        — name of the derived predicate, e.g. "sharesLanguage"
    head_args    : list[str]  — variables for the head, e.g. ["X", "Y"]
    body         : list[str]  — each element is a complete Prolog goal, e.g. "officialLanguage(X, L)"
    comment      : str        — optional inline comment
    """

    head_functor: str
    head_args: list[str]
    body: list[str]
    comment: str = ""

    def render(self) -> str:
        head = f"{self.head_functor}({', '.join(self.head_args)})"
        body = ", ".join(self.body)
        return f"{head} :- {body}."


@dataclass
class RuleGroup:
    """A named group of rules rendered under one comment header."""

    label: str
    rules: list[Rule]

    def render(self) -> list[str]:
        lines = []
        for rule in self.rules:
            lines.append(rule.render())
        lines.append("")
        return lines


# ---------------------------------------------------------------------------
# Country data
# ---------------------------------------------------------------------------

COUNTRIES: list[Country] = [
    # --- Europe ---
    Country(
        "spain",
        "europe",
        "euro",
        ["spanish"],
        "madrid",
        cities=["barcelona"],
        borders=["portugal", "france"],
        memberships=["nato", "eu", "g20"],
    ),
    Country(
        "france",
        "europe",
        "euro",
        ["french"],
        "paris",
        borders=["spain", "germany", "italy", "switzerland", "belgium"],
        memberships=["nato", "eu", "g20"],
    ),
    Country(
        "germany",
        "europe",
        "euro",
        ["german"],
        "berlin",
        borders=["france", "switzerland", "belgium"],
        memberships=["nato", "eu", "g20"],
    ),
    Country(
        "italy",
        "europe",
        "euro",
        ["italian"],
        "rome",
        borders=["france", "switzerland"],
        memberships=["nato", "eu", "g20"],
    ),
    Country(
        "portugal",
        "europe",
        "euro",
        ["portuguese"],
        "lisbon",
        borders=["spain"],
        memberships=["nato", "eu"],
    ),
    Country(
        "switzerland",
        "europe",
        "swissFranc",
        ["german", "french", "italian"],
        "bern",
        cities=["zurich"],
        borders=["france", "germany", "italy"],
    ),
    Country(
        "belgium",
        "europe",
        "euro",
        ["french", "dutch"],
        "brussels",
        borders=["france", "germany"],
        memberships=["nato", "eu"],
    ),
    Country(
        "united_kingdom",
        "europe",
        "pound",
        ["english"],
        "london",
        memberships=["nato", "aukus", "g20", ],
    ),
    Country(
        "netherlands",
        "europe",
        "euro",
        ["dutch"],
        "amsterdam",
        cities=["rotterdam"],
        borders=["belgium", "germany"],
        memberships=["nato", "eu", "g20"],
    ),
    Country(
        "denmark",
        "europe",
        "danish_krone",
        ["danish"],
        "copenhagen",
        cities=["aarhus"],
        borders=["germany"],
        memberships=["nato", "eu", "g20"],
    ),
    Country(
        "norway",
        "europe",
        "norwegian_krone",
        ["norwegian"],
        "oslo",
        cities=["bergen"],
        borders=["sweden"],
        memberships=["nato"],
    ),
    Country(
        "sweden",
        "europe",
        "swedish_krone",
        ["swedish"],
        "stockholm",
        cities=["gothenburg"],
        borders=["norway", "finland"],
        memberships=["eu", "g20"],
    ),
    Country(
        "finland",
        "europe",
        "euro",
        ["finnish", "swedish"],
        "helsinki",
        cities=["tampere"],
        borders=["sweden"],
        memberships=["eu"],
    ),
    Country(
        "poland",
        "europe",
        "zloty",
        ["polish"],
        "warsaw",
        cities=["krakow"],
        borders=["germany", "czechia"],
        memberships=["eu", "nato", "g20"],
    ),
    Country(
        "czechia",
        "europe",
        "koruna",
        ["czech"],
        "prague",
        cities=["brno"],
        borders=["germany", "poland", "austria", "slovakia"],
        memberships=["eu", "nato"],
    ),
    Country(
        "austria",
        "europe",
        "euro",
        ["german"],
        "vienna",
        cities=["salzburg"],
        borders=["germany", "czechia", "hungary", "italy"],
        memberships=["eu", "nato"],
    ),
    Country(
        "hungary",
        "europe",
        "forint",
        ["hungarian"],
        "budapest",
        cities=["debrecen"],
        borders=["austria", "slovakia", "romania"],
        memberships=["eu", "nato"],
    ),
    Country(
        "ireland",
        "europe",
        "euro",
        ["english", "irish"],
        "dublin",
        cities=["cork"],
        memberships=["eu", "g20"],
    ),
    Country(
        "romania",
        "europe",
        "romanian_leu",
        ["romanian"],
        "bucharest",
        cities=["cluj_napoca"],
        borders=["hungary", "bulgaria"],
        memberships=["eu", "nato"],
    ),
    Country(
        "greece",
        "europe",
        "euro",
        ["greek"],
        "athens",
        cities=["thessaloniki"],
        borders=["bulgaria"],
        memberships=["eu", "nato"],
    ),
    Country(
        "belarus",
        "europe",
        "belarusian_ruble",
        ["belarusian", "russian"],
        "minsk",
        cities=["gomel"],
        borders=["poland", "ukraine"],
        memberships=["cis"],
    ),
    Country(
        "bulgaria",
        "europe",
        "lev",
        ["bulgarian"],
        "sofia",
        cities=["plovdiv"],
        borders=["romania", "greece", "turkey"],
        memberships=["eu", "nato"],
    ),
    Country(
        "ukraine",
        "europe",
        "hryvnia",
        ["ukrainian"],
        "kyiv",
        cities=["kharkiv"],
        borders=["poland"],
    ),
    Country(
        "croatia",
        "europe",
        "euro",
        ["croatian"],
        "zagreb",
        cities=["split"],
        borders=["hungary"],
        memberships=["eu", "nato"],
    ),
    Country(
        "slovakia",
        "europe",
        "euro",
        ["slovak"],
        "bratislava",
        cities=["kosice"],
        borders=["czechia", "austria", "hungary", "poland"],
        memberships=["eu", "nato"],
    ),
    Country(
        "slovenia",
        "europe",
        "euro",
        ["slovenian"],
        "ljubljana",
        cities=["maribor"],
        borders=["austria", "croatia"],
        memberships=["eu", "nato"],
    ),
    Country(
        "serbia",
        "europe",
        "serbian_dinar",
        ["serbian"],
        "belgrade",
        cities=["novi_sad"],
        borders=["hungary", "bulgaria", "croatia"],
    ),
    Country(
        "albania",
        "europe",
        "lek",
        ["albanian"],
        "tirana",
        cities=["durres"],
    ),
    Country(
        "andorra",
        "europe",
        "euro",
        ["catalan"],
        "andorra_la_vella",
    ),
    Country(
        "armenia",
        "europe",
        "dram",
        ["armenian"],
        "yerevan",
        cities=["gyumri"],
        memberships=["cis"],
    ),
    Country(
        "azerbaijan",
        "europe",
        "azerbaijani_manat",
        ["azerbaijani"],
        "baku",
        cities=["ganja"],
        memberships=["cis"],
    ),
    Country(
        "bosnia_and_herzegovina",
        "europe",
        "mark",
        ["bosnian", "croatian", "serbian"],
        "sarajevo",
        cities=["mostar"],
    ),
    Country(
        "cyprus",
        "europe",
        "euro",
        ["greek", "turkish"],
        "nicosia",
        cities=["limassol"],
    ),
    Country(
        "estonia",
        "europe",
        "euro",
        ["estonian"],
        "tallinn",
        cities=["tartu"],
    ),
    Country(
        "georgia",
        "europe",
        "lari",
        ["georgian"],
        "tbilisi",
        cities=["batumi"],
    ),
    Country(
        "iceland",
        "europe",
        "krona",
        ["icelandic"],
        "reykjavik",
        cities=["akureyri"],
    ),
    Country(
        "latvia",
        "europe",
        "euro",
        ["latvian"],
        "riga",
        cities=["daugavpils"],
    ),
    Country(
        "liechtenstein",
        "europe",
        "swissFranc",
        ["german"],
        "vaduz",
    ),
    Country(
        "lithuania",
        "europe",
        "euro",
        ["lithuanian"],
        "vilnius",
        cities=["kaunas"],
    ),
    Country(
        "luxembourg",
        "europe",
        "euro",
        ["luxembourgish", "french", "german"],
        "luxembourg_city",
    ),
    Country(
        "malta",
        "europe",
        "euro",
        ["maltese", "english"],
        "valletta",
    ),
    Country(
        "moldova",
        "europe",
        "moldovan_leu",
        ["romanian"],
        "chisinau",
        cities=["balti"],
        memberships=["cis"],
    ),
    Country(
        "monaco",
        "europe",
        "euro",
        ["french"],
        "monaco",
    ),
    Country(
        "montenegro",
        "europe",
        "euro",
        ["montenegrin"],
        "podgorica",
        cities=["niksic"],
    ),
    Country(
        "north_macedonia",
        "europe",
        "denar",
        ["macedonian", "albanian"],
        "skopje",
        cities=["bitola"],
    ),
    Country(
        "russia",
        "europe",
        "russian_ruble",
        ["russian"],
        "moscow",
        cities=["st_petersburg"],
        memberships=["cis", "brics"],
    ),
    Country(
        "san_marino",
        "europe",
        "euro",
        ["italian"],
        "san_marino",
    ),
    Country(
        "kosovo",
        "europe",
        "euro",
        ["albanian", "serbian"],
        "pristina",
    ),
    Country(
        "vatican_city",
        "europe",
        "euro",
        ["italian", "latin"],
        "vatican_city",
    ),
    Country(
        "palestine",
        "middle_east",
        "shekel",
        ["arabic"],
        "ramallah",
    ),
    # --- North America ---
    Country(
        "united_states",
        "north_america",
        "usd",
        ["english"],
        "washington_dc",
        cities=["new_york_city"],
        borders=["canada", "mexico"],
        memberships=["nato", "aukus", "g20", "usmca"],
    ),
    Country(
        "canada",
        "north_america",
        "cad",
        ["english", "french"],
        "ottawa",
        borders=["united_states"],
        memberships=["nato", "g20", "usmca", ],
    ),
    Country(
        "mexico",
        "north_america",
        "mxn",
        ["spanish"],
        "mexico_city",
        borders=["united_states"],
        memberships=["g20", "usmca"],
    ),
    Country(
        "guatemala",
        "north_america",
        "quetzal",
        ["spanish"],
        "guatemala_city",
        cities=["quetzaltenango"],
        borders=["mexico"],
    ),
    Country(
        "costa_rica",
        "north_america",
        "colon",
        ["spanish"],
        "san_jose",
        cities=["liberia"],
        borders=["panama"],
    ),
    Country(
        "panama",
        "north_america",
        "balboa",
        ["spanish"],
        "panama_city",
        cities=["colon"],
        borders=["costa_rica"],
    ),
    Country(
        "cuba",
        "north_america",
        "cuban_peso",
        ["spanish"],
        "havana",
        cities=["santiago_de_cuba"],
    ),
    Country(
        "jamaica",
        "north_america",
        "jamaican_dollar",
        ["english"],
        "kingston",
        cities=["mandeville"],
        memberships=[],
    ),
    Country(
        "belize",
        "north_america",
        "belize_dollar",
        ["english"],
        "belmopan",
        cities=["belize_city"],
        borders=["guatemala"],
    ),
    Country(
        "honduras",
        "north_america",
        "lempira",
        ["spanish"],
        "tegucigalpa",
        cities=["san_pedro_sula"],
        borders=["guatemala"],
    ),
    Country(
        "nicaragua",
        "north_america",
        "cordoba",
        ["spanish"],
        "managua",
        cities=["leon"],
        borders=["costa_rica"],
    ),
    Country(
        "el_salvador",
        "north_america",
        "usd",
        ["spanish"],
        "san_salvador",
        cities=["santa_ana"],
        borders=["guatemala"],
    ),
    Country(
        "haiti",
        "north_america",
        "gourde",
        ["french", "haitian_creole"],
        "port_au_prince",
        cities=["cap_haitien"],
    ),
    Country(
        "dominican_republic",
        "north_america",
        "dominican_peso",
        ["spanish"],
        "santo_domingo",
        cities=["santiago_de_los_caballeros"],
    ),
    Country(
        "antigua_and_barbuda",
        "north_america",
        "eastern_caribbean_dollar",
        ["english"],
        "saint_johns",
    ),
    Country(
        "bahamas",
        "north_america",
        "bahamian_dollar",
        ["english"],
        "nassau",
    ),
    Country(
        "barbados",
        "north_america",
        "barbados_dollar",
        ["english"],
        "bridgetown",
    ),
    Country(
        "dominica",
        "north_america",
        "eastern_caribbean_dollar",
        ["english"],
        "roseau",
    ),
    Country(
        "grenada",
        "north_america",
        "eastern_caribbean_dollar",
        ["english"],
        "st_georges",
    ),
    Country(
        "saint_kitts_and_nevis",
        "north_america",
        "eastern_caribbean_dollar",
        ["english"],
        "basseterre",
    ),
    Country(
        "saint_lucia",
        "north_america",
        "eastern_caribbean_dollar",
        ["english"],
        "castries",
    ),
    Country(
        "saint_vincent_and_the_grenadines",
        "north_america",
        "eastern_caribbean_dollar",
        ["english"],
        "kingstown",
    ),
    Country(
        "trinidad_and_tobago",
        "north_america",
        "trinidad_and_tobago_dollar",
        ["english"],
        "port_of_spain",
    ),
    # --- Asia ---
    Country(
        "japan",
        "asia",
        "yen",
        ["japanese"],
        "tokyo",
        cities=["osaka"],
        memberships=["g20"],
    ),
    Country(
        "india",
        "asia",
        "indian_rupee",
        ["hindi", "english"],
        "new_delhi",
        cities=["mumbai"],
        memberships=["g20", "brics"],
    ),
    Country(
        "china",
        "asia",
        "yuan",
        ["chinese"],
        "beijing",
        cities=["shanghai"],
        borders=["india"],
        memberships=["g20", "brics"],
    ),
    Country(
        "south_korea",
        "asia",
        "south_korean_won",
        ["korean"],
        "seoul",
        cities=["busan"],
        memberships=["g20"],
    ),
    Country(
        "north_korea",
        "asia",
        "north_korean_won",
        ["korean"],
        "pyongyang",
        cities=["cheonjin"],
    ),
    Country(
        "thailand",
        "asia",
        "baht",
        ["thai"],
        "bangkok",
        cities=["chiang_mai"],
        borders=["malaysia"],
    ),
    Country(
        "vietnam",
        "asia",
        "dong",
        ["vietnamese"],
        "hanoi",
        cities=["ho_chi_minh_city"],
        borders=["china"],
    ),
    Country(
        "indonesia",
        "asia",
        "rupiah",
        ["indonesian"],
        "jakarta",
        cities=["surabaya"],
        memberships=["g20", "brics"],
    ),
    Country(
        "pakistan",
        "asia",
        "pakistani_rupee",
        ["urdu", "english"],
        "islamabad",
        cities=["karachi"],
        borders=["india"],
        memberships=["g20"],
    ),
    Country(
        "bangladesh",
        "asia",
        "taka",
        ["bengali"],
        "dhaka",
        cities=["chittagong"],
        borders=["india"],
        memberships=["g20"],
    ),
    Country(
        "malaysia",
        "asia",
        "ringgit",
        ["malay"],
        "kuala_lumpur",
        cities=["penang"],
        borders=["thailand"],
        memberships=["g20"],
    ),
    Country(
        "singapore",
        "asia",
        "singapore_dollar",
        ["english", "malay", "mandarin"],
        "singapore_city",
    ),
    Country(
        "afghanistan",
        "asia",
        "afghani",
        ["pashto", "dari"],
        "kabul",
        cities=["kandahar"],
        borders=["pakistan"],
    ),
    Country(
        "nepal",
        "asia",
        "nepali_rupee",
        ["nepali"],
        "kathmandu",
        cities=["pokhara"],
        borders=["india"],
    ),
    Country(
        "laos",
        "asia",
        "kip",
        ["lao"],
        "vientiane",
        cities=["pakse"],
        borders=["thailand", "vietnam"],
    ),
    Country(
        "philippines",
        "asia",
        "philippine_peso",
        ["filipino", "english"],
        "manila",
        cities=["cebu_city"],
    ),
    Country(
        "bahrain",
        "middle_east",
        "bahraini_dinar",
        ["arabic", "english"],
        "manama",
    ),
    Country(
        "bhutan",
        "asia",
        "ngultrum",
        ["dzongkha"],
        "thimphu",
    ),
    Country(
        "brunei",
        "asia",
        "brunei_dollar",
        ["malay", "english"],
        "bandar_seri_begawan",
    ),
    Country(
        "cambodia",
        "asia",
        "riel",
        ["khmer"],
        "phnom_penh",
        cities=["siem_reap"],
    ),
    Country(
        "kazakhstan",
        "asia",
        "tenge",
        ["kazakh", "russian"],
        "astana",
        cities=["almaty"],
        memberships=["cis"],
    ),
    Country(
        "kyrgyzstan",
        "asia",
        "kyrgyz_som",
        ["kyrgyz", "russian"],
        "bishkek",
        memberships=["cis"],
    ),
    Country(
        "maldives",
        "asia",
        "rufiyaa",
        ["dhivehi"],
        "male",
    ),
    Country(
        "mongolia",
        "asia",
        "tugrik",
        ["mongolian"],
        "ulaanbaatar",
    ),
    Country(
        "myanmar",
        "asia",
        "kyat",
        ["burmese"],
        "naypyidaw",
        cities=["yangon"],
    ),
    Country(
        "sri_lanka",
        "asia",
        "sri_lankan_rupee",
        ["sinhala", "tamil"],
        "sri_jayawardenepura_kotte",
        cities=["colombo"],
    ),
    Country(
        "tajikistan",
        "asia",
        "tajik_somoni",
        ["tajik"],
        "dushanbe",
        memberships=["cis"],
    ),
    Country(
        "timor_leste",
        "asia",
        "usd",
        ["tetum", "portuguese"],
        "dili",
    ),
    Country(
        "taiwan",
        "asia",
        "new_taiwan_dollar",
        ["mandarin"],
        "taipei",
        cities=["kaohsiung"],
    ),
    Country(
        "turkmenistan",
        "asia",
        "turkmen_manat",
        ["turkmen"],
        "ashgabat",
    ),
    Country(
        "uzbekistan",
        "asia",
        "uzbek_som",
        ["uzbek"],
        "tashkent",
        memberships=["cis"],
    ),
    # --- Africa ---
    Country(
        "south_africa",
        "africa",
        "rand",
        ["english", "afrikaans"],
        "cape_town",
        memberships=["g20", "brics"],
    ),
    Country("nigeria", "africa", "naira", ["english"], "abuja"),
    Country(
        "egypt",
        "africa",
        "egyptian_pound",
        ["arabic"],
        "cairo",
        cities=["alexandria"],
        memberships=["g20", "brics"],
    ),
    Country(
        "kenya",
        "africa",
        "kenyan_shilling",
        ["english", "swahili"],
        "nairobi",
        cities=["mombasa"],
    ),
    Country(
        "ethiopia",
        "africa",
        "birr",
        ["amharic"],
        "addis_ababa",
        cities=["dire_dawa"],
        memberships=["brics"],
    ),
    Country(
        "ghana",
        "africa",
        "cedi",
        ["english"],
        "accra",
        cities=["kumasi"],
    ),
    Country(
        "morocco",
        "africa",
        "moroccan_dirham",
        ["arabic"],
        "rabat",
        cities=["casablanca"],
    ),
    Country(
        "algeria",
        "africa",
        "algerian_dinar",
        ["arabic"],
        "algiers",
        cities=["oran"],
        borders=["morocco", "tunisia"],
    ),
    Country(
        "tunisia",
        "africa",
        "tunisian_dinar",
        ["arabic"],
        "tunis",
        cities=["sfax"],
        borders=["algeria"],
    ),
    Country(
        "uganda",
        "africa",
        "ugandan_shilling",
        ["english", "swahili"],
        "kampala",
        cities=["jinja"],
    ),
    Country(
        "tanzania",
        "africa",
        "tanzanian_shilling",
        ["swahili", "english"],
        "dodoma",
        cities=["dar_es_salaam"],
    ),
    Country(
        "rwanda",
        "africa",
        "rwandan_franc",
        ["kinyarwanda", "english"],
        "kigali",
        cities=["butare"],
    ),
    Country(
        "senegal",
        "africa",
        "cfa_franc",
        ["french"],
        "dakar",
        cities=["thies"],
    ),
    Country(
        "cameroon",
        "africa",
        "cfa_franc",
        ["french", "english"],
        "yaounde",
        cities=["douala"],
    ),
    Country(
        "zimbabwe",
        "africa",
        "zimbabwe_dollar",
        ["english", "shona"],
        "harare",
        cities=["bulawayo"],
    ),
    Country(
        "angola",
        "africa",
        "kwanza",
        ["portuguese"],
        "luanda",
        cities=["lobito"],
    ),
    Country(
        "benin",
        "africa",
        "cfa_franc",
        ["french"],
        "porto_novo",
        cities=["cotonou"],
    ),
    Country(
        "botswana",
        "africa",
        "pula",
        ["english", "setswana"],
        "gaborone",
    ),
    Country(
        "burkina_faso",
        "africa",
        "cfa_franc",
        ["french"],
        "ouagadougou",
    ),
    Country(
        "burundi",
        "africa",
        "burundian_franc",
        ["kirundi", "french"],
        "gitega",
    ),
    Country(
        "cape_verde",
        "africa",
        "escudo",
        ["portuguese"],
        "praia",
    ),
    Country(
        "central_african_republic",
        "africa",
        "cfa_franc",
        ["french", "sango"],
        "bangui",
    ),
    Country(
        "chad",
        "africa",
        "cfa_franc",
        ["french", "arabic"],
        "ndjamena",
    ),
    Country(
        "congo",
        "africa",
        "cfa_franc",
        ["french"],
        "brazzaville",
    ),
    Country(
        "cote_divoire",
        "africa",
        "cfa_franc",
        ["french"],
        "yamoussoukro",
        cities=["abidjan"],
    ),
    Country(
        "djibouti",
        "africa",
        "djiboutian_franc",
        ["french", "arabic"],
        "djibouti",
    ),
    Country(
        "equatorial_guinea",
        "africa",
        "cfa_franc",
        ["spanish", "french", "portuguese"],
        "malabo",
    ),
    Country(
        "eritrea",
        "africa",
        "nakfa",
        ["tigrinya", "arabic", "english"],
        "asmara",
    ),
    Country(
        "eswatini",
        "africa",
        "lilangeni",
        ["swati", "english"],
        "mbabane",
    ),
    Country(
        "gabon",
        "africa",
        "cfa_franc",
        ["french"],
        "libreville",
    ),
    Country(
        "gambia",
        "africa",
        "dalasi",
        ["english"],
        "banjul",
    ),
    Country(
        "guinea",
        "africa",
        "guinean_franc",
        ["french"],
        "conakry",
    ),
    Country(
        "guinea_bissau",
        "africa",
        "cfa_franc",
        ["portuguese", "crioulo"],
        "bissau",
    ),
    Country(
        "lesotho",
        "africa",
        "loti",
        ["sotho", "english"],
        "maseru",
    ),
    Country(
        "liberia",
        "africa",
        "liberian_dollar",
        ["english"],
        "monrovia",
    ),
    Country(
        "madagascar",
        "africa",
        "ariary",
        ["malagasy", "french"],
        "antananarivo",
    ),
    Country(
        "malawi",
        "africa",
        "malawian_kwacha",
        ["english", "chichewa"],
        "lilongwe",
    ),
    Country(
        "mali",
        "africa",
        "cfa_franc",
        ["french"],
        "bamako",
    ),
    Country(
        "mauritania",
        "africa",
        "ouguiya",
        ["arabic"],
        "nouakchott",
    ),
    Country(
        "mauritius",
        "africa",
        "mauritian_rupee",
        ["english", "french"],
        "port_louis",
    ),
    Country(
        "mozambique",
        "africa",
        "metical",
        ["portuguese"],
        "maputo",
    ),
    Country(
        "namibia",
        "africa",
        "namibian_dollar",
        ["english"],
        "windhoek",
    ),
    Country(
        "niger",
        "africa",
        "cfa_franc",
        ["french"],
        "niamey",
    ),
    Country(
        "sao_tome_and_principe",
        "africa",
        "dobra",
        ["portuguese"],
        "sao_tome",
    ),
    Country(
        "seychelles",
        "africa",
        "seychellois_rupee",
        ["creole", "english", "french"],
        "victoria",
    ),
    Country(
        "sierra_leone",
        "africa",
        "leone",
        ["english"],
        "freetown",
    ),
    Country(
        "sudan",
        "africa",
        "sudanese_pound",
        ["arabic", "english"],
        "khartoum",
    ),
    Country(
        "togo",
        "africa",
        "cfa_franc",
        ["french"],
        "lome",
    ),
    Country(
        "zambia",
        "africa",
        "zambian_kwacha",
        ["english"],
        "lusaka",
    ),
    Country(
        "libya",
        "africa",
        "libyan_dinar",
        ["arabic"],
        "tripoli",
        cities=["banghazi"],
        borders=["egypt", "algeria", "tunisia"],
    ),
    Country(
        "south_sudan",
        "africa",
        "south_sudanese_pound",
        ["english"],
        "juba",
        cities=["wau"],
        borders=["uganda", "ethiopia", "kenya"],
    ),
    Country(
        "dr_congo",
        "africa",
        "congolese_franc",
        ["french"],
        "kinshasa",
        cities=["lubumbashi"],
        borders=["uganda", "rwanda"],
    ),
    Country(
        "somalia",
        "africa",
        "somali_shilling",
        ["somali", "arabic"],
        "mogadishu",
        cities=["kismayo"],
        borders=["ethiopia"],
    ),
    # --- Middle East ---
    Country(
        "saudi_arabia",
        "middle_east",
        "saudi_riyal",
        ["arabic"],
        "riyadh",
        memberships=["g20", "gcc", "brics"],
    ),
    Country(
        "united_arab_emirates",
        "middle_east",
        "uae_dirham",
        ["arabic"],
        "abu_dhabi",
        memberships=["gcc", "brics"],
    ),
    Country(
        "qatar",
        "middle_east",
        "qatari_riyal",
        ["arabic"],
        "doha",
        cities=["al_wakrah"],
        borders=["saudi_arabia", "united_arab_emirates"],
        memberships=["gcc"],
    ),
    Country(
        "kuwait",
        "middle_east",
        "kuwaiti_dinar",
        ["arabic"],
        "kuwait_city",
        cities=["hawalli"],
        borders=["saudi_arabia"],
        memberships=["gcc"],
    ),
    Country(
        "oman",
        "middle_east",
        "omani_rial",
        ["arabic"],
        "muscat",
        cities=["salalah"],
        borders=["saudi_arabia", "united_arab_emirates"],
        memberships=["gcc"],
    ),
    Country(
        "jordan",
        "middle_east",
        "jordanian_dinar",
        ["arabic"],
        "amman",
        cities=["aqaba"],
        borders=["israel", "saudi_arabia"],
    ),
    Country(
        "israel",
        "middle_east",
        "shekel",
        ["hebrew", "arabic"],
        "jerusalem",
        cities=["tel_aviv"],
        borders=["jordan"],
    ),
    Country(
        "iran",
        "middle_east",
        "iranian_rial",
        ["persian"],
        "tehran",
        cities=["mashhad"],
        borders=["iraq", "pakistan"],
        memberships=["brics"],
    ),
    Country(
        "iraq",
        "middle_east",
        "iraqi_dinar",
        ["arabic", "kurdish"],
        "baghdad",
        cities=["basra"],
        borders=["iran", "jordan"],
    ),
    Country(
        "turkey",
        "middle_east",
        "lira",
        ["turkish"],
        "ankara",
        cities=["istanbul"],
        borders=["greece", "bulgaria"],
    ),
    Country(
        "lebanon",
        "middle_east",
        "lebanese_pound",
        ["arabic"],
        "beirut",
        cities=["tripoli"],
    ),
    Country(
        "syria",
        "middle_east",
        "syrian_pound",
        ["arabic"],
        "damascus",
        cities=["aleppo"],
        borders=["turkey", "israel", "jordan", "iraq", "lebanon"],
    ),
    Country(
        "yemen",
        "middle_east",
        "yemeni_rial",
        ["arabic"],
        "sanaa",
        cities=["aden"],
        borders=["saudi_arabia", "oman"],
    ),
    # --- Oceania ---
    Country(
        "australia",
        "oceania",
        "aud",
        ["english"],
        "canberra",
        cities=["sydney"],
        memberships=["aukus", "g20", ],
    ),
    Country(
        "new_zealand",
        "oceania",
        "new_zealand_dollar",
        ["english", "maori"],
        "wellington",
        cities=["auckland"],
        memberships=[],
    ),
    Country(
        "fiji",
        "oceania",
        "fiji_dollar",
        ["english", "fijian"],
        "suva",
        cities=["nadi"],
        memberships=[],
    ),
    Country(
        "papua_new_guinea",
        "oceania",
        "kina",
        ["english", "tok_pisin"],
        "port_moresby",
        cities=["lae"],
    ),
    Country(
        "samoa",
        "oceania",
        "tala",
        ["samoan", "english"],
        "apia",
        cities=["avai"],
    ),
    Country(
        "tonga",
        "oceania",
        "paanga",
        ["tongan", "english"],
        "nukualofa",
        cities=["neiafu"],
    ),
    Country(
        "vanuatu",
        "oceania",
        "vatu",
        ["bislama", "english", "french"],
        "port_vila",
        cities=["luganville"],
    ),
    Country(
        "solomon_islands",
        "oceania",
        "solomon_islands_dollar",
        ["english"],
        "honiara",
        cities=["gizo"],
    ),
    Country(
        "kiribati",
        "oceania",
        "aud",
        ["english", "gilbertese"],
        "tarawa",
    ),
    Country(
        "marshall_islands",
        "oceania",
        "usd",
        ["english", "marshallese"],
        "majuro",
    ),
    Country(
        "micronesia",
        "oceania",
        "usd",
        ["english"],
        "palikir",
    ),
    Country(
        "nauru",
        "oceania",
        "aud",
        ["nauruan", "english"],
        "yaren",
    ),
    Country(
        "palau",
        "oceania",
        "usd",
        ["palauan", "english"],
        "ngerulmud",
    ),
    # --- South America ---
    Country(
        "brazil",
        "south_america",
        "real",
        ["portuguese"],
        "brasilia",
        cities=["sao_paulo"],
        memberships=["g20", "brics"],
    ),
    Country(
        "argentina",
        "south_america",
        "argentine_peso",
        ["spanish"],
        "buenos_aires",
        cities=["cordoba"],
        borders=["chile"],
        memberships=["g20"],
    ),
    Country(
        "chile",
        "south_america",
        "chilean_peso",
        ["spanish"],
        "santiago",
        cities=["valparaiso"],
        borders=["argentina", "peru"],
        memberships=["g20"],
    ),
    Country(
        "colombia",
        "south_america",
        "colombian_peso",
        ["spanish"],
        "bogota",
        cities=["medellin"],
        borders=["venezuela", "ecuador", "peru"],
        memberships=["g20"],
    ),
    Country(
        "peru",
        "south_america",
        "sol",
        ["spanish"],
        "lima",
        cities=["cusco"],
        borders=["chile", "colombia"],
        memberships=["g20"],
    ),
    Country(
        "uruguay",
        "south_america",
        "uruguayan_peso",
        ["spanish"],
        "montevideo",
        cities=["salto"],
        borders=["argentina", "brazil"],
        memberships=["g20"],
    ),
    Country(
        "ecuador",
        "south_america",
        "usd",
        ["spanish"],
        "quito",
        cities=["guayaquil"],
        borders=["colombia", "peru"],
    ),
    Country(
        "venezuela",
        "south_america",
        "bolivar",
        ["spanish"],
        "caracas",
        cities=["maracaibo"],
        borders=["colombia"],
    ),
    Country(
        "bolivia",
        "south_america",
        "boliviano",
        ["spanish", "quechua"],
        "sucre",
        cities=["la_paz"],
        borders=["peru", "brazil"],
    ),
    Country(
        "paraguay",
        "south_america",
        "guarani",
        ["spanish", "guarani"],
        "asuncion",
        cities=["ciudad_del_este"],
        borders=["argentina", "brazil"],
    ),
    Country(
        "guyana",
        "south_america",
        "guyanese_dollar",
        ["english"],
        "georgetown",
        cities=["linden"],
        borders=["brazil"],
    ),
    Country(
        "suriname",
        "south_america",
        "surinamese_dollar",
        ["dutch"],
        "paramaribo",
        cities=["nieuw_nickerie"],
        borders=["brazil"],
    ),
]


# Border overrides fill in obvious omissions from the lightweight country data
# above without forcing every country definition to spell out a long neighbor list.
BORDER_OVERRIDES: dict[str, list[str]] = {
    # Europe
    "albania": ["greece", "kosovo", "montenegro", "north_macedonia"],
    "andorra": ["france", "spain"],
    "armenia": ["georgia", "azerbaijan", "iran", "turkey"],
    "azerbaijan": ["armenia", "georgia", "iran", "russia"],
    "bosnia_and_herzegovina": ["croatia", "montenegro", "serbia"],
    "estonia": ["latvia", "russia"],
    "georgia": ["armenia", "azerbaijan", "russia", "turkey"],
    "latvia": ["estonia", "lithuania", "belarus", "russia"],
    "liechtenstein": ["austria", "switzerland"],
    "lithuania": ["latvia", "belarus", "poland", "russia"],
    "luxembourg": ["belgium", "france", "germany"],
    "moldova": ["romania", "ukraine"],
    "monaco": ["france"],
    "montenegro": ["albania", "bosnia_and_herzegovina", "croatia", "kosovo", "serbia"],
    "north_macedonia": ["albania", "bulgaria", "greece", "kosovo", "serbia"],
    "russia": [
        "norway",
        "finland",
        "estonia",
        "latvia",
        "lithuania",
        "poland",
        "belarus",
        "ukraine",
        "georgia",
        "azerbaijan",
        "kazakhstan",
        "china",
        "mongolia",
        "north_korea",
    ],
    "san_marino": ["italy"],
    "kosovo": ["albania", "montenegro", "north_macedonia", "serbia"],
    "vatican_city": ["italy"],
    # North America / Caribbean
    "mexico": ["united_states", "guatemala", "belize"],
    "guatemala": ["mexico", "belize", "honduras", "el_salvador"],
    "costa_rica": ["nicaragua", "panama"],
    "panama": ["costa_rica", "colombia"],
    "belize": ["guatemala", "mexico"],
    "honduras": ["guatemala", "el_salvador", "nicaragua"],
    "el_salvador": ["guatemala", "honduras"],
    "nicaragua": ["honduras", "costa_rica"],
    # Asia
    "india": ["pakistan", "china", "nepal", "bhutan", "bangladesh", "myanmar"],
    "south_korea": ["north_korea"],
    "north_korea": ["south_korea", "china", "russia"],
    "bhutan": ["china", "india"],
    "cambodia": ["thailand", "laos", "vietnam"],
    "china": [
        "india",
        "pakistan",
        "afghanistan",
        "tajikistan",
        "kyrgyzstan",
        "kazakhstan",
        "russia",
        "mongolia",
        "north_korea",
        "vietnam",
        "laos",
        "myanmar",
        "nepal",
        "bhutan",
    ],
    "kazakhstan": ["russia", "china", "kyrgyzstan", "uzbekistan", "turkmenistan"],
    "kyrgyzstan": ["kazakhstan", "china", "uzbekistan", "tajikistan"],
    "mongolia": ["russia", "china"],
    "myanmar": ["india", "bangladesh", "china", "laos", "thailand"],
    "tajikistan": ["afghanistan", "china", "kyrgyzstan", "uzbekistan"],
    "turkmenistan": ["kazakhstan", "uzbekistan", "afghanistan", "iran"],
    "uzbekistan": ["kazakhstan", "kyrgyzstan", "tajikistan", "afghanistan", "turkmenistan"],
    "timor_leste": ["indonesia"],
    "taiwan": [],
    # Africa
    "south_africa": ["namibia", "botswana", "zimbabwe", "mozambique", "eswatini", "lesotho"],
    "nigeria": ["niger", "chad", "cameroon", "benin"],
    "egypt": ["libya", "sudan", "israel", "palestine"],
    "kenya": ["uganda", "tanzania", "ethiopia", "south_sudan", "somalia"],
    "ethiopia": ["eritrea", "djibouti", "somalia", "kenya", "south_sudan", "sudan"],
    "ghana": ["cote_divoire", "burkina_faso", "togo"],
    "morocco": ["algeria"],
    "uganda": ["south_sudan", "kenya", "tanzania", "rwanda", "dr_congo"],
    "tanzania": ["kenya", "uganda", "rwanda", "burundi", "dr_congo", "zambia", "malawi", "mozambique"],
    "rwanda": ["uganda", "tanzania", "burundi", "dr_congo"],
    "senegal": ["mauritania", "mali", "guinea", "guinea_bissau", "gambia"],
    "cameroon": ["nigeria", "chad", "central_african_republic", "equatorial_guinea", "gabon", "congo"],
    "zimbabwe": ["south_africa", "botswana", "namibia", "zambia", "mozambique"],
    "angola": ["namibia", "zambia", "dr_congo", "congo"],
    "benin": ["togo", "burkina_faso", "niger", "nigeria"],
    "botswana": ["south_africa", "namibia", "zimbabwe", "zambia"],
    "burkina_faso": ["mali", "niger", "benin", "togo", "ghana", "cote_divoire"],
    "burundi": ["rwanda", "tanzania", "dr_congo"],
    "central_african_republic": ["chad", "sudan", "south_sudan", "cameroon", "congo", "dr_congo"],
    "chad": ["libya", "sudan", "central_african_republic", "cameroon", "nigeria", "niger"],
    "congo": ["gabon", "cameroon", "central_african_republic", "dr_congo", "angola"],
    "cote_divoire": ["liberia", "guinea", "mali", "burkina_faso", "ghana"],
    "djibouti": ["eritrea", "ethiopia", "somalia"],
    "equatorial_guinea": ["cameroon", "gabon"],
    "eritrea": ["sudan", "ethiopia", "djibouti"],
    "eswatini": ["south_africa", "mozambique"],
    "gabon": ["cameroon", "equatorial_guinea", "congo"],
    "gambia": ["senegal"],
    "guinea": ["senegal", "mali", "cote_divoire", "liberia", "sierra_leone", "guinea_bissau"],
    "guinea_bissau": ["senegal", "guinea"],
    "lesotho": ["south_africa"],
    "liberia": ["sierra_leone", "guinea", "cote_divoire"],
    "malawi": ["tanzania", "mozambique", "zambia"],
    "mali": ["algeria", "niger", "burkina_faso", "cote_divoire", "guinea", "senegal", "mauritania"],
    "mauritania": ["senegal", "mali"],
    "mozambique": ["tanzania", "malawi", "zambia", "zimbabwe", "south_africa", "eswatini"],
    "namibia": ["angola", "zambia", "botswana", "south_africa"],
    "niger": ["algeria", "libya", "chad", "nigeria", "benin", "burkina_faso", "mali"],
    "sierra_leone": ["guinea", "liberia"],
    "sudan": ["egypt", "libya", "chad", "central_african_republic", "south_sudan", "ethiopia", "eritrea"],
    "togo": ["ghana", "burkina_faso", "benin"],
    "zambia": ["tanzania", "dr_congo", "angola", "zimbabwe", "botswana", "namibia", "malawi", "mozambique"],
    # Middle East
    "saudi_arabia": ["jordan", "iraq", "kuwait", "united_arab_emirates", "oman", "yemen"],
    "united_arab_emirates": ["saudi_arabia", "oman"],
    "lebanon": ["syria", "israel"],
    "palestine": ["israel", "egypt"],
    # Oceania
    "papua_new_guinea": ["indonesia"],
    # South America
    "argentina": ["bolivia", "brazil", "chile", "paraguay", "uruguay"],
    "bolivia": ["argentina", "brazil", "chile", "paraguay", "peru"],
    "brazil": [
        "argentina",
        "bolivia",
        "colombia",
        "guyana",
        "paraguay",
        "peru",
        "suriname",
        "uruguay",
        "venezuela",
    ],
    "chile": ["argentina", "bolivia", "peru"],
    "colombia": ["brazil", "ecuador", "panama", "peru", "venezuela"],
    "ecuador": ["colombia", "peru"],
    "guyana": ["brazil", "suriname", "venezuela"],
    "paraguay": ["argentina", "bolivia", "brazil"],
    "peru": ["bolivia", "brazil", "chile", "colombia", "ecuador"],
    "suriname": ["brazil", "guyana"],
    "uruguay": ["argentina", "brazil"],
    "venezuela": ["brazil", "colombia", "guyana"],
}


# ---------------------------------------------------------------------------
# Rule data
# ---------------------------------------------------------------------------


def _region_rules(countries: list[Country]) -> RuleGroup:
    """Auto-generate one countryIn<Region> rule per unique region found in data."""
    regions = sorted({c.region for c in countries})
    rules = []
    for region in regions:
        # e.g. north_america → countryInNorthAmerica
        functor = "countryIn" + "".join(w.capitalize() for w in region.split("_"))
        rules.append(
            Rule(
                head_functor=functor,
                head_args=["Country"],
                body=[f"locatedIn(Country, {region})"],
            )
        )
    return RuleGroup("Country-in-region helpers (auto-generated from data)", rules)


RULE_GROUPS: list[RuleGroup] = [
    RuleGroup(
        "Shared-attribute rules",
        [
            Rule(
                "usesSameCurrency", ["X", "Y"], ["currencyOf(X, C)", "currencyOf(Y, C)"]
            ),
            Rule(
                "sharesLanguage",
                ["X", "Y"],
                ["officialLanguage(X, L)", "officialLanguage(Y, L)"],
            ),
            Rule("sameRegion", ["X", "Y"], ["locatedIn(X, R)", "locatedIn(Y, R)"]),
            Rule("sameAlliance", ["X", "Y"], ["memberOf(X, O)", "memberOf(Y, O)"]),
        ],
    ),
    RuleGroup(
        "City / capital location rules",
        [
            Rule(
                "cityInContinent",
                ["City", "Continent"],
                ["cityIn(City, Country)", "locatedIn(Country, Continent)"],
            ),
            Rule(
                "cityInRegion",
                ["City", "Region"],
                ["cityIn(City, Country)", "locatedIn(Country, Region)"],
            ),
            Rule("capitalCity", ["City"], ["capitalOf(Country, City)"]),
            Rule(
                "capitalInContinent",
                ["City", "Continent"],
                ["capitalOf(Country, City)", "locatedIn(Country, Continent)"],
            ),
            Rule(
                "capitalInAlliance",
                ["City", "Org"],
                ["capitalOf(Country, City)", "memberOf(Country, Org)"],
            ),
            Rule(
                "cityInAlliance",
                ["City", "Org"],
                ["cityIn(City, Country)", "memberOf(Country, Org)"],
            ),
        ],
    ),
    RuleGroup(
        "Eurozone rules",
        [
            Rule("isEurozone", ["Country"], ["currencyOf(Country, euro)"]),
            Rule(
                "eurozoneCity",
                ["City"],
                ["cityIn(City, Country)", "isEurozone(Country)"],
            ),
        ],
    ),
    RuleGroup(
        "Border rules",
        [
            Rule(
                "sharesBorder",
                ["X", "Y"],
                ["borders(X, Y)"],
                comment="undirected — clause 1",
            ),
            Rule(
                "sharesBorder",
                ["X", "Y"],
                ["borders(Y, X)"],
                comment="undirected — clause 2",
            ),
            Rule(
                "twoBorderTrip",
                ["X", "Z"],
                ["sharesBorder(X, Y)", "sharesBorder(Y, Z)"],
            ),
            Rule(
                "borderingEurozone",
                ["X", "Y"],
                ["sharesBorder(X, Y)", "isEurozone(X)", "isEurozone(Y)"],
            ),
            Rule(
                "threeBorderTrip",
                ["X", "W"],
                ["twoBorderTrip(X, Y)", "sharesBorder(Y, W)"],
            ),
            Rule(
                "fourBorderTrip",
                ["X", "V"],
                ["threeBorderTrip(X, Y)", "sharesBorder(Y, V)"],
            ),
        ],
    ),
    RuleGroup(
        "Alliance + region compound rules",
        [
            Rule(
                "countryInAllianceAndRegion",
                ["Country", "Org", "Region"],
                ["memberOf(Country, Org)", "locatedIn(Country, Region)"],
            ),
            Rule(
                "cityInAllianceAndRegion",
                ["City", "Org", "Region"],
                [
                    "cityIn(City, Country)",
                    "memberOf(Country, Org)",
                    "locatedIn(Country, Region)",
                ],
            ),
            Rule(
                "capitalInAllianceAndRegion",
                ["City", "Org", "Region"],
                [
                    "capitalOf(Country, City)",
                    "memberOf(Country, Org)",
                    "locatedIn(Country, Region)",
                ],
            ),
            Rule(
                "borderNeighborAlliance",
                ["Country", "Org"],
                ["sharesBorder(Country, Neighbor)", "memberOf(Neighbor, Org)"],
            ),
            Rule(
                "twoStepBorderNeighborAlliance",
                ["Country", "Org"],
                ["twoBorderTrip(Country, Neighbor)", "memberOf(Neighbor, Org)"],
            ),
        ],
    ),
    # _region_rules(COUNTRIES) is appended dynamically in main()
]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------


def generate_facts(countries: list[Country]) -> list[str]:
    def fact(functor: str, *args) -> str:
        return f"{functor}({', '.join(args)})."

    sections: dict[str, list[str]] = {
        "locatedIn": [],
        "currencyOf": [],
        "officialLanguage": [],
        "cityIn": [],
        "capitalOf": [],
        "borders": [],
        "memberOf": [],
    }
    seen_borders: set[frozenset] = set()

    for c in countries:
        sections["locatedIn"].append(fact("locatedIn", c.name, c.region))
        sections["currencyOf"].append(fact("currencyOf", c.name, c.currency))
        for lang in c.languages:
            sections["officialLanguage"].append(fact("officialLanguage", c.name, lang))
        sections["capitalOf"].append(fact("capitalOf", c.name, c.capital))
        sections["cityIn"].append(fact("cityIn", c.capital, c.name))
        for city in c.cities:
            sections["cityIn"].append(fact("cityIn", city, c.name))
        neighbors = sorted(set(c.borders) | set(BORDER_OVERRIDES.get(c.name, [])))
        for neighbor in neighbors:
            pair = frozenset({c.name, neighbor})
            if pair not in seen_borders:
                sections["borders"].append(fact("borders", c.name, neighbor))
                seen_borders.add(pair)
        for org in c.memberships:
            sections["memberOf"].append(fact("memberOf", c.name, org))

    lines = []
    for section, facts in sections.items():
        if facts:
            lines.extend(facts)
            lines.append("")
    return lines


def generate_rules(groups: list[RuleGroup]) -> list[str]:
    lines = []
    for group in groups:
        lines.extend(group.render())
    return lines


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    output_path = "countries_kb.txt"

    all_groups = RULE_GROUPS + [_region_rules(COUNTRIES)]

    fact_lines = generate_facts(COUNTRIES)
    rule_lines = generate_rules(all_groups)

    with open(output_path, "w") as f:
        f.write("\n".join(fact_lines))
        f.write("\n".join(rule_lines))

    print(f"Written to {output_path}")
    print(f"  {sum(1 for l in fact_lines if l.endswith('.'))} facts")
    print(f"  {sum(1 for l in rule_lines if ':-' in l)} rules")


if __name__ == "__main__":
    main()

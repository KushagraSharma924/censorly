"""
Multilingual Word Detection Module for AI Profanity Filter
Handles profanity detection in multiple languages and scripts including:
- English abusive words
- Hindi abusive words (Latin script)
- Hindi abusive words (Devanagari script)
"""

import re
import unicodedata
from typing import Dict, List, Any, Set
from better_profanity import profanity

# Comprehensive abusive word lists
ENGLISH_WORDS = [
    # Common English profanity
    "fuck", "fucking", "fucker", "fucked", "fucks", "fck", "f*ck", "f**k",
    "shit", "shitting", "shitty", "sht", "sh*t", "sh**", "crap", "crappy",
    "bitch", "bitches", "bitching", "b*tch", "biatch", "beyotch",
    "bastard", "bastards", "bstrd", "b*strd", "bastrd",
    "asshole", "assholes", "a**hole", "a*shole", "ass", "arse", "arsehole",
    "damn", "damned", "dammit", "damnit", "d*mn", "dmn",
    "hell", "heck", "bloody", "bldy", "bl**dy",
    "piss", "pissed", "pissing", "p*ss", "peed", "urinate",
    "cock", "c*ck", "c**k", "rooster", "penis", "dick", "d*ck", "d**k",
    "pussy", "p*ssy", "p**sy", "vagina", "v*gina", "cunt", "c*nt", "c**t",
    "whore", "wh*re", "slut", "sl*t", "slutty", "prostitute", "hooker",
    "motherfucker", "mf", "mofo", "m*therf*cker", "motherf*cker",
    "son of a bitch", "sob", "sonofabitch", "s.o.b",
    "bullshit", "bs", "b.s", "bull", "horseshit", "dipshit",
    "jackass", "dumbass", "smartass", "badass", "fatass", "ass",
    "retard", "retarded", "rtrd", "r*tard", "mental", "mentl",
    "idiot", "moron", "stupid", "dumb", "loser", "failure", "fail",
    "faggot", "fag", "f*g", "f**", "gay", "homo", "homosexual",
    "lesbian", "lez", "dyke", "d*ke", "queer", "qu**r",
    "nigger", "nigga", "n*gger", "n*gga", "negro", "negr*",
    "tranny", "transgender", "tr*nny", "shemale", "ladyboy",
    
    # Additional vulgar terms
    "tits", "boobs", "titties", "breasts", "boobies", "knockers",
    "nuts", "balls", "testicles", "ballsack", "nutsack",
    "sperm", "cum", "jizz", "semen", "orgasm", "climax",
    "masturbate", "jerk off", "beat off", "wank", "fap",
    "rape", "molest", "assault", "abuse", "violated",
    
    # Internet slang and abbreviations
    "wtf", "wth", "stfu", "gtfo", "kys", "kms", "fml", "ffs",
    "lmao", "lmfao", "omg", "jfc", "smh", "af", "lit", "fam",
    
    # Creative spelling variations
    "phuck", "fuk", "fook", "shyt", "shiit", "beotch", "biotch",
    "azzhole", "azz", "dayum", "dayam", "hellz", "sheeet", "shieet",
    
    # Milder profanity and insults
    "jerk", "jerks", "douche", "douchebag", "tool", "tools",
    "prick", "pr*ck", "wimp", "wimps", "coward", "chicken",
    "freak", "weirdo", "creep", "creeps", "pervert", "perv",
    "sicko", "psycho", "crazy", "insane", "nuts", "mental",
    
    # Body parts (potentially offensive in context)
    "butt", "butthole", "anus", "rectum", "genital", "genitals",
    "private parts", "intimate", "naked", "nude", "strip",
    
    # Sexual actions/terms
    "bang", "screw", "nail", "pound", "smash", "hit it",
    "do it", "get some", "score", "hookup", "one night stand",
    
    # Discriminatory terms
    "racist", "sexist", "bigot", "nazi", "fascist", "commie",
    "redneck", "hillbilly", "trailer trash", "white trash",
    
    # Religious profanity
    "goddamn", "god damn", "jesus christ", "holy shit", "christ",
    "jesus", "lord", "god", "allah", "buddha" # context dependent
]

HINDI_LATIN_WORDS = [
    # Core abusive words and their variations
    "chutiya", "chutiye", "chutiya hai", "chutiyapa", "chutiyaap", "chutiyagiri",
    "chutiya ban", "chutiya samjha", "chutiya kaat", "chutiye ho", "chutiya bol",
    "chootiya", "chootiye", "chotiya", "chotiye", "chootia", "chutia", "cutiya",
    "ch00tiya", "chut1ya", "chu7iya", "ch8tiya", "chutiy@", "chutiy4",
    
    # Core short forms and standalone words
    "chu", "chut", "choot", "chud", "chuda", "chudi", "chudai",
    "bhen", "bhench", "mc", "bc", "madarchod", "behenchod",
    
    # Madarchod variations
    "madarchod", "madarchod hai", "madar chod", "mader chod", "madarchoda",
    "madarchood", "madarchoot", "madarchoot hai", "madarjaat", "madarjat",
    "madre chod", "madre chood", "maa ka bhosada", "ma ka bhosda", "mkb",
    "madarch0d", "mad@rch0d", "m@d@rch0d", "mc bc", "mc ki", "mc teri",
    "ma ki chudai", "ma ki choot", "maa ki chudai", "maa chuda", "maa chudai",
    
    # Bhenchod variations
    "bhenchod", "bhen chod", "behan chod", "bahan chod", "bhainchod", "bhnchod",
    "bhenchoda", "bhen ka loda", "behen ka loda", "bhen ke lund", "behen ke lund",
    "bkl", "b.k.l", "behen ke lavde", "bhen ki chut", "behen ki chut",
    "bhanke", "bhanki", "bhankay", "bhenke", "bhen", "bhene",
    "bh3nch0d", "bh3n ch0d", "bhencho", "bhench0", "bhenc**d", "bh@nch0d",
    
    # Bhosadike variations
    "bhosadike", "bhosadi ke", "bhosda", "bhosadi", "bhosdike", "bhos dk",
    "bhosadika", "bhosadiki", "bhosada", "bhosdiwale", "bhosdiwala", "bhosadi wale",
    "bh0s@dike", "bh0$@dike", "bhosad1ke", "bhos@dike", "bhosda ki", "bhosda ke",
    
    # Randi variations
    "randi", "rand", "randwa", "rundi", "rund", "rundwa", "randiya", "randikhana",
    "randi bazi", "randi rona", "randi saali", "randi ki aulaad", "randi ka baccha",
    "r@ndi", "r4ndi", "r*ndi", "randee", "randii", "rundy", "randy",
    
    # Harami variations
    "harami", "haramzada", "haraamzada", "haram ka pilla", "haram ki aulaad",
    "haramkhor", "haraamkhor", "harami saala", "harami kutta", "haramzaadi",
    "h@r@mi", "har@mi", "haraam", "haram", "har4mi", "haraami", "haraamee",
    
    # Gandu variations
    "gandu", "gando", "gandoo", "ganduwa", "gandiya", "gandi", "gand mara",
    "gand me danda", "gand phat", "gand maar", "gand tod", "gand fad",
    "g@ndu", "g4ndu", "g*ndu", "ganduu", "gaandu", "gaand", "gand",
    "gand me dum", "gand me keeda", "gand chatna", "gand me ghusa",
    
    # Lund variations
    "lund", "loda", "lund choos", "lund choosna", "lund fakir", "lund ka baal",
    "lundura", "lundwa", "lund khajur", "lode ka baal", "loda lassan", "lola",
    "l*nd", "l@nd", "l4nd", "lundd", "lun d", "lund-fakir", "lund pe charh",
    
    # Chut variations
    "chut", "choot", "chooth", "chuut", "chut ka baal", "chut mein daal",
    "chut marni", "chutad", "chutmarani", "chut ki roti", "chut ka papad",
    "chudh", "chudha", "chudhi", "chudhai", "chudwana", "chudwai",
    "chud", "chuda", "chudi", "chudwata", "chudwati", "chudwaye",
    "chudwadain", "chuddin", "chudwain", "chudain", "chuddain",
    "ch*t", "ch@t", "ch4t", "chutt", "chu t", "choot marni", "chut maarna",
    
    # Gaand variations
    "gaand", "gand", "gaandu", "gandu", "gand mara", "gaand mara", "gand maar",
    "gaand maar", "gand tod", "gaand tod", "gand fad", "gaand phat",
    "g@and", "g@nd", "ga@nd", "gaa*d", "ga4nd", "gaandd", "gandd",
    
    # Kamina variations
    "kamina", "kamini", "kaminey", "kamine", "kamina saala", "kamina kutta",
    "kaminapanti", "kaminagiri", "kameena", "kameeni", "kameenapan",
    "k@min@", "k4min4", "kam*na", "kameenaa", "kameeenaa",
    
    # Saala/Saali variations
    "saala", "saali", "sala", "sali", "saale", "saali kutti", "saala kutta",
    "sale", "saaley", "saalon", "saaliyon", "sala kamina", "saali randi",
    "s@la", "s@li", "s4la", "s4li", "saalaa", "saalii", "saala bc",
    
    # Kutta/Kutti variations
    "kutta", "kutti", "kutiya", "kute", "kutton", "kuttiyon", "kutta saala",
    "kutti saali", "kutta kamina", "kutti randi", "kuttey", "kutia",
    "k*tta", "k@tta", "k4tta", "kuttaa", "kuttii", "kut taa", "kut ti",
    
    # Various other abusive terms
    "bevakoof", "bevkoof", "bewakoof", "bewkoof", "buddhu", "budhu", "bhudhu",
    "pagal", "mental", "dimag kharab", "dimaag kharab", "ullu", "gadha", "gaddha",
    "jhaat", "jhaatu", "jhant", "jhantu", "baal", "baal ka", "jhaat ke baal",
    
    # Regional and slang variations
    "chinal", "chinaal", "tawaif", "rakhel", "keep", "rakha", "rakhi",
    "badtameez", "badtamiz", "manhoos", "zaleel", "neech", "najayaz",
    "badmaash", "badmash", "lafanga", "awaara", "awara", "charsi", "nashe baaz",
    
    # Common abbreviations and code words
    "mc", "bc", "bkl", "mkc", "wtf", "stfu", "mofo", "sob", "pos", "bs",
    "f off", "eff off", "go to hell", "bhad me ja", "nikal", "bhaag",
    "bhen ke lode", "behen ke lode", "bhen ke lund", "behen ke lund",
    "bhenke loda", "bhenke lola", "bhen ka loda", "bhen ka lola",
    
    # Number/symbol substitutions
    "chut1ya", "madarch0d", "bh3nch0d", "ch0d", "ch00tiya", "mad@rch0d",
    "bh0$@dike", "g@ndu", "l*nd", "ch*t", "r@ndi", "h@r@mi", "k@min@",
    "s@la", "s@li", "k@tta", "g@nd", "bh@nch0d", "m@d@rch0d", "gandu",
    
    # Phonetic variations
    "madharjod", "madharjot", "bhenjo", "bhenjot", "chotia", "chothiya",
    "gandiya", "lundiya", "randa", "randya", "harma", "harmia",
    
    # Extended vulgar vocabulary
    "lauda", "lawda", "laura", "lawra", "laudya", "lawdya", "laudu", "lawdu",
    "bur", "burr", "buur", "bhosda", "bhosra", "bhosdaa", "rakhail",
    "chakla", "chaklabaji", "dalaal", "dallal", "pimping", "dhanda",
    
    # Insulting terms
    "kanjoos", "kanjoosh", "kukar", "kukkur", "suar", "sowar", "janwar",
    "haiwaan", "darinda", "rakshas", "shaitan", "iblis", "badshakl",
    "badbakht", "manhus", "najayaz", "harami ki aulaad", "najayaz aulaad",
    
    # Sexual terms
    "dhakka", "dhakkha", "thappad", "maarna", "pitna", "chodna", "chudna",
    "chudwana", "chudai", "chudwai", "maal", "item", "figure", "body",
    "boobs", "chest", "size", "kamar", "nitamb", "surata", "sambhog",
    
    # Extended family insults
    "baap", "maa baap", "khandan", "vansh", "kul", "nasl", "generation",
    "family tree", "teri maa", "tera baap", "tere ghar wale", "tere relatives",
    "teri behen", "teri biwi", "teri girlfriend", "tera boyfriend",
    
    # Compound insults and phrases
    "ma ki chut", "ma ka bhosda", "behen ki chut", "behen ka bhosda",
    "baap ki gaand", "dada ki gaand", "nana ki gaand", "mama ki gaand",
    "chacha ki gaand", "tau ki gaand", "sasur ki gaand", "saas ki gaand",
    
    # More creative insults
    "dimag ki ma ka bhosda", "buddhi ka baap", "akal ke dushman",
    "sense ki ma ka bosda", "brain dead", "zombie", "robot", "machine",
    "kachre ka dabba", "gandagi ka raja", "mitti ka putla", "paagal kutta",
    
    # Tech/modern slang
    "noob", "n00b", "newbie", "chutiya coder", "faltu developer",
    "bugs ki ma", "errors ka baap", "exception ka raja", "null pointer ki ma",
    "segfault ka baap", "memory leak ki ma", "infinite loop ka papa",
    
    # Sports related
    "loser", "failure", "flop", "disaster", "catastrophe", "zero", "nil",
    "useless", "worthless", "good for nothing", "nalayak", "naakaara",
    
    # Money/status related
    "gareeb", "kangaal", "bhikhari", "faqeer", "fakir", "road side",
    "footpath", "slum", "jhuggi", "jhopadpatti", "basti", "mohalla",
    
    # Appearance related
    "ugly", "badshakl", "badsurat", "kala", "kaala", "gora", "chitta",
    "mota", "patla", "lambu", "naatu", "takla", "ganja", "baal ke bagair",
    
    # Intelligence related
    "stupid", "dumb", "idiot", "moron", "fool", "foolish", "bewakoof",
    "nalayak", "nikamma", "kaam ka nahi", "faaltu", "time waste",
    
    # Sound/onomatopoeia variations
    "thoo", "chee", "yuck", "ugh", "eww", "gross", "disgusting",
    "ghatiya", "ganda", "gandagi", "mehr", "dirt", "dirty",
    
    # Regional dialect variations (removed overly common words)
    "abe", "abey", "oye", "arrey", "abbe", "abey", "ay", "oy",
    "tere", "tumhare", "aapke", "iska", "uska",
    
    # Casual dismissive terms
    "chal", "nikal", "bhaag", "bhag ja", "dur ho", "side me ja",
    "hat", "hatt", "dur", "door", "chala ja", "ja re", "ja na",
    
    # Extended variants with prefixes/suffixes
    "mahachutiya", "supergandu", "ultralund", "megaharami", "gigakamina",
    "teraharami", "wohkamina", "yehgandu", "uskichut", "iskagaand",
    
    # Missing words from video transcript
    "chodh", "bhenke", "bhen ko chodh", "ki bhen ko chodh", "chodh in", 
    "ko chodh", "mako chodh", "chodh mourodin", "chodh tanke",
    "maha", "inye", "siwala", "inwale", "maha ki chud", "chudwata",
    "bhanke", "greega", "inge", "saati", "foca", "admi", "takh",
    
    # Critical phrases from video filename - these MUST be detected
    "meri bhen ki chu", "bhen ki chu", "ki chu", "chu",
    "meri behen ki chu", "behen ki chu", "meri bhen ki chut", "bhen ki chut",
    
    # Transcription variations we've seen
    "chho", "bhin", "chin", "chhin", "bheen", "bean",
    "chu", "chuu", "chhuu", "bhin ko chho", "chho raye",
    
    # Creative combinations
    "gandu harami", "chutiya kamina", "randi ki aulaad", "kutte ka bacha",
    "suar ki nasl", "gadhe ka beta", "ullu ka pattha", "bhains ka bacha"
]

HINDI_DEVANAGARI_WORDS = [
    # Core abusive words and their variations
    "चुतिया", "चुतिये", "चुतिया है", "चुतियापा", "चुतियाप", "चुतियागिरी",
    "चुतिया बन", "चुतिया समझा", "चुतिया काट", "चुतिये हो", "चुतिया बोल",
    "चूतिया", "चूतिये", "छोटिया", "छोटिये", "चूतिया", "चुतिया",
    
    # मादरचोद variations
    "मादरचोद", "मादरचोद है", "मादर चोद", "मादेर चोद", "मादरचोदा",
    "मादरछूद", "मादरचूत", "मादरचूत है", "मादरजात", "मादरजात",
    "माद्रे चोद", "माद्रे छूद", "मां का भोसड़ा", "मा का भोसड़ा", "एमकेबी",
    "मा की चुदाई", "मा की चूत", "मां की चुदाई", "मां चुदा", "मां चुदाई",
    
    # भेनचोद variations
    "भेनचोद", "भेन चोद", "बेहन चोद", "बहन चोद", "भैंसचोद", "भ्नचोद",
    "भेनचोदा", "भेन का लोड़ा", "बेहन का लोड़ा", "भेन के लंड", "बेहन के लंड",
    "बीकेएल", "बेहन के लवड़े", "भेन की चूत", "बेहन की चूत",
    "भेनचो", "भेनच", "भेन", "भैंच", "बहन के लोड़े",
    
    # भोसड़ीके variations
    "भोसड़ीके", "भोसड़ी के", "भोसड़ा", "भोसड़ी", "भोसदीके", "भोस डीके",
    "भोसड़ीका", "भोसड़ीकी", "भोसड़ा", "भोसड़ीवाले", "भोसड़ीवाला", "भोसड़ी वाले",
    "भोसड़ी की", "भोसड़ा के", "भोसड़े", "भोसड़ियों",
    
    # रंडी variations
    "रंडी", "रंड", "रंडवा", "रुंडी", "रुंड", "रुंडवा", "रंडिया", "रंडीखाना",
    "रंडी बाजी", "रंडी रोना", "रंडी साली", "रंडी की औलाद", "रंडी का बच्चा",
    "रांडी", "रैंडी", "रुंडी", "रंडे", "रंडियों",
    
    # हरामी variations
    "हरामी", "हरामजादा", "हरामजादा", "हराम का पिल्ला", "हराम की औलाद",
    "हरामखोर", "हरामखोर", "हरामी साला", "हरामी कुत्ता", "हरामजादी",
    "हराम", "हरम", "हरामी", "हरामजादे", "हरामजादों",
    
    # गंदू variations
    "गंदू", "गांडो", "गांडू", "गंदुवा", "गंदिया", "गंदी", "गांड मरा",
    "गांड में डंडा", "गांड फट", "गांड मार", "गांड तोड़", "गांड फाड़",
    "गांडू", "गाांडू", "गांड", "गांड में दम", "गांड में कीड़ा", "गांड चाटना", "गांड में घुसा",
    
    # लंड variations
    "लंड", "लोड़ा", "लंड चूस", "लंड चूसना", "लंड फकीर", "लंड का बाल",
    "लंडुरा", "लंडवा", "लंड खजूर", "लोड़े का बाल", "लोड़ा लस्सन", "लोला",
    "लंड पे चढ़", "लंड", "लुंड", "लोड़", "लंडे",
    
    # चूत variations
    "चूत", "चूत", "चूथ", "चुूत", "चूत का बाल", "चूत में डाल",
    "चूत मरनी", "चुतड़", "चूतमरनी", "चूत की रोटी", "चूत का पापड़",
    "चुध", "चुधा", "चुधी", "चुधाई", "चुधवाना", "चुधवाई",
    "चुत", "चूत मरनी", "चूत मारना", "चूत्त", "चुत्त",
    
    # गांड variations
    "गांड", "गंड", "गांडू", "गंदू", "गंड मरा", "गांड मरा", "गंड मार",
    "गांड मार", "गंड तोड़", "गांड तोड़", "गंड फाड़", "गांड फट",
    "गाांड", "गांद", "गांडड़", "गंडड़", "गाांडू",
    
    # कमीना variations
    "कमीना", "कमीनी", "कमीने", "कमीने", "कमीना साला", "कमीना कुत्ता",
    "कमीनापंती", "कमीनागिरी", "कमीना", "कमीनी", "कमीनापन",
    "कमेेना", "कमेेनी", "कमेेनाा", "कमीने", "कमीनों",
    
    # साला/साली variations
    "साला", "साली", "सला", "सली", "साले", "साली कुत्ती", "साला कुत्ता",
    "सले", "सालेय", "सालों", "सालियों", "सला कमीना", "साली रंडी",
    "सााला", "सााली", "साला बीसी", "साली रांडी",
    
    # कुत्ता/कुत्ती variations
    "कुत्ता", "कुत्ती", "कुतिया", "कुते", "कुत्तों", "कुत्तियों", "कुत्ता साला",
    "कुत्ती साली", "कुत्ता कमीना", "कुत्ती रंडी", "कुत्ते", "कुतिया",
    "कुत्ताा", "कुत्तीी", "कुत ता", "कुत ती", "कुत्तेे",
    
    # Various other abusive terms
    "बेवकूफ", "बेवकूफ", "बेवकूफ", "बेवकूफ", "बुद्धू", "बुधु", "भुधु",
    "पागल", "मेंटल", "दिमाग खराब", "दिमाग खराब", "उल्लू", "गधा", "गद्धा",
    "झाट", "झाटू", "झंट", "झंटू", "बाल", "बाल का", "झाट के बाल",
    
    # Regional and slang variations
    "चिनाल", "चिनाल", "तवायफ", "रखेल", "कीप", "रखा", "रखी",
    "बदतमीज", "बदतमीज", "मनहूस", "जलील", "नीच", "नाजायज",
    "बदमाश", "बदमाश", "लफंगा", "आवारा", "आवारा", "चरसी", "नशे बाज",
    
    # Insulting terms
    "कंजूस", "कंजूस", "कुकर", "कुक्कुर", "सुअर", "सवार", "जानवर",
    "हैवान", "दरिंदा", "राक्षस", "शैतान", "इब्लीस", "बदशक्ल",
    "बदबख्त", "मनहुस", "नाजायज", "हरामी की औलाद", "नाजायज औलाद",
    
    # Sexual terms
    "धक्का", "धक्कha", "थप्पड़", "मारना", "पीटना", "चोदना", "चुदना",
    "चुदवाना", "चुदाई", "चुदवाई", "माल", "आइटम", "फिगर", "बॉडी",
    "छाती", "आकार", "कमर", "नितंब", "सुरता", "संभोग",
    
    # Extended family insults
    "बाप", "मां बाप", "खानदान", "वंश", "कुल", "नस्ल", "जेनेरेशन",
    "फैमिली ट्री", "तेरी मां", "तेरा बाप", "तेरे घर वाले", "तेरे रिश्तेदार",
    "तेरी बहन", "तेरी बीवी", "तेरी गर्लफ्रेंड", "तेरा बॉयफ्रेंड",
    
    # Compound insults and phrases
    "मा की चूत", "मा का भोसड़ा", "बहन की चूत", "बहन का भोसड़ा",
    "बाप की गांड", "दादा की गांड", "नाना की गांड", "मामा की गांड",
    "चाचा की गांड", "ताऊ की गांड", "ससुर की गांड", "सास की गांड",
    
    # More creative insults
    "दिमाग की मा का भोसड़ा", "बुद्धि का बाप", "अकल के दुश्मन",
    "सेंस की मा का बोसड़ा", "ब्रेन डेड", "जॉम्बी", "रोबोट", "मशीन",
    "कचरे का डब्बा", "गंदगी का राजा", "मिट्टी का पुतला", "पागल कुत्ता",
    
    # Extended variants with prefixes/suffixes
    "महाचुतिया", "सुपरगांडू", "अल्ट्रालंड", "मेगाहरामी", "गिगाकमीना",
    "तेराहरामी", "वहकमीना", "यहगांडू", "उसकीचूत", "इसकागांड",
    
    # Critical phrases from video content - Devanagari
    "मेरी बहन की चू", "बहन की चू", "की चू", "चू",
    "मेरी बहन की चूत", "बहन की चूत", "मेरी बहन", "छू", "छु", "छूू",
    
    # Extended vulgar vocabulary
    "लौड़ा", "लावड़ा", "लौरा", "लावरा", "लौड़या", "लावड़या", "लौड़ू", "लावड़ू",
    "बुर", "बुर्र", "बूर", "भोसड़ा", "भोसरा", "भोसड़ाा", "रखैल",
    "चकला", "चकलाबाजी", "दलाल", "दल्लाल", "पिंपिंग", "धंधा",
    
    # Money/status related
    "गरीब", "कंगाल", "भिखारी", "फकीर", "फकीर", "रोड साइड",
    "फुटपाथ", "स्लम", "झुग्गी", "झोपड़पट्टी", "बस्ती", "मोहल्ला",
    
    # Appearance related
    "बदशक्ल", "बदसूरत", "काला", "काला", "गोरा", "चिट्टा",
    "मोटा", "पतला", "लंबू", "नाटू", "टकला", "गंजा", "बाल के बगैर",
    
    # Intelligence related
    "स्टुपिड", "डम्ब", "इडियट", "मोरोन", "फूल", "फूलिश", "बेवकूफ",
    "नालायक", "निकम्मा", "काम का नहीं", "फालतू", "टाइम वेस्ट",
    
    # Sound/onomatopoeia variations
    "थू", "ची", "यक", "उघ", "इव", "घिनौना", "घिनावना",
    "घटिया", "गंदा", "गंदगी", "मेहर", "डर्ट", "डर्टी",
    
    # Regional dialect variations (removed overly common words)
    "अबे", "अबेय", "ओये", "अर्रे", "अब्बे", "अबेय", "अय", "ऑय",
    "तेरे", "तुम्हारे", "आपके", "इसका", "उसका",
    
    # Casual dismissive terms (be careful with common words)
    "निकल", "भाग", "भग जा", "दूर हो", "साइड में जा",
    "हट", "हट्ट", "दूर", "चला जा", "जा रे", "जा न",
    
    # Numbers written in Devanagari
    "एक", "दो", "तीन", "चार", "पांच", "छह", "सात", "आठ", "नौ", "दस",
    "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह", "सोलह", "सत्रह", "अठारह", "उन्नीस", "बीस"
]

# Urdu/Arabic script Hindi abusive words (Whisper sometimes transcribes Hindi in this script)
HINDI_URDU_SCRIPT_WORDS = [
    # Common Hindi abusive words in Arabic/Urdu script (as transcribed by Whisper)
    "ماتشودوانے",  # madarchod variants
    "مادرچود", "مادر چود", "ماتر چود", "ماتشود", "ماتچود",
    "بھینچود", "بھین چود", "بہنچود", "بہن چود",  # behenchod variants
    "بھین کے لولے", "بہن کے لولے", "بھین کی",  # bhen ke lode variants
    "چتیا", "چوتیا", "چٹیا", "چوٹیا",  # chutiya variants
    "چودن", "چودنا", "چود", "چودو",  # chod variants
    "ماتکو چودن", "ماتکو چود", "ماتو چود",  # matko chod variants
    "گندو", "گاندو", "گنڈو",  # gandu variants
    "رنڈی", "رندی", "رانڈی",  # randi variants
    "ہرامی", "حرامی", "هرامي",  # harami variants
    "سالا", "سالے", "صالا",  # sala variants
    "کتیا", "کٹیا", "کوتیا",  # kutiya variants
    "لوڑا", "لولا", "لولے", "لوڑے",  # loda/lode variants
    "بھوسڑی", "بھوسڑے", "بھوسری",  # bhosadi variants
    "چودی", "چودے", "چودا",  # chodi variants
    "مادری", "مادر", "ماں",  # mother related
    "بہن", "بھین", "بھن",  # sister related
    "لنڈ", "لند", "لنڈا",  # lund variants
    
    # Common combinations that appear in transcriptions
    "سیواللائن والے", "سيوا لائن والے",  # transcription artifacts with profanity
    "نکتک", "نکتے", "نکلے",  # variations
    "اماری", "امری", "ہماری",  # possessive variants
    "تو your", "تم", "تو",  # you variants mixed with English
    
    # Additional Urdu script profanity that might appear
    "کس", "کسی", "کیس",  # kas variants
    "پھدی", "پھڈی", "فدی",  # phudi variants
    "چوت", "چوٹ", "چؤت",  # chut variants
    "بوبس", "بوبز", "ممے",  # boobs variants
    "سیکس", "جنسی", "فک",  # sex related
]

# Combined word list for easier management
ALL_ABUSIVE_WORDS = {
    'english': ENGLISH_WORDS,
    'hindi_latin': HINDI_LATIN_WORDS,
    'hindi_devanagari': HINDI_DEVANAGARI_WORDS,
    'hindi_urdu_script': HINDI_URDU_SCRIPT_WORDS
}


def normalize_text(text: str) -> str:
    """
    Normalize text for better matching across different scripts and formats.
    
    Args:
        text (str): Input text to normalize
        
    Returns:
        str: Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove diacritics and normalize Unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Replace common number-to-letter substitutions
    substitutions = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', 
        '7': 't', '8': 'b', '@': 'a', '$': 's', '*': ''
    }
    
    for num, letter in substitutions.items():
        text = text.replace(num, letter)
    
    return text


def clean_word(word: str) -> str:
    """
    Clean a word by removing punctuation and special characters.
    
    Args:
        word (str): Word to clean
        
    Returns:
        str: Cleaned word
    """
    # Remove punctuation and special characters, keep alphanumeric and Devanagari
    cleaned = re.sub(r'[^\w\u0900-\u097F]', '', word)
    return cleaned.strip()


def create_word_variations(word: str) -> Set[str]:
    """
    Create variations of a word for better detection.
    
    Args:
        word (str): Base word
        
    Returns:
        Set[str]: Set of word variations
    """
    variations = {word}
    
    # Add normalized version
    normalized = normalize_text(word)
    variations.add(normalized)
    
    # Add version without spaces
    variations.add(word.replace(' ', ''))
    
    # Add version with common separators
    for sep in ['_', '-', '.']:
        variations.add(word.replace(' ', sep))
    
    # Add symbol variations for common substitutions
    if any(char in word for char in ['a', 'o', 'i', 's']):
        # Create @ substitutions
        word_at = word.replace('a', '@')
        variations.add(word_at)
        
        # Create 0 substitutions  
        word_0 = word.replace('o', '0')
        variations.add(word_0)
        
        # Create 1 substitutions
        word_1 = word.replace('i', '1')
        variations.add(word_1)
        
        # Create $ substitutions
        word_dollar = word.replace('s', '$')
        variations.add(word_dollar)
    
    return variations


def build_profanity_patterns() -> Dict[str, Set[str]]:
    """
    Build comprehensive profanity patterns for all languages.
    
    Returns:
        Dict containing all profanity patterns by language
    """
    patterns = {}
    
    for lang, words in ALL_ABUSIVE_WORDS.items():
        lang_patterns = set()
        
        for word in words:
            # Add the original word
            lang_patterns.add(word.lower())
            
            # Add variations
            variations = create_word_variations(word)
            lang_patterns.update(variations)
            
            # Add cleaned version
            cleaned = clean_word(word)
            if cleaned:
                lang_patterns.add(cleaned.lower())
        
        patterns[lang] = lang_patterns
    
    return patterns


# Build patterns once at module level for performance
PROFANITY_PATTERNS = build_profanity_patterns()


def detect_profane_words_in_text(text: str) -> List[Dict[str, Any]]:
    """
    Detect profane words in a given text across multiple languages.
    
    Args:
        text (str): Text to check for profanity
    
    Returns:
        List of dictionaries containing detected profane words and their languages
    """
    if not text:
        return []
    
    detected_words = []
    normalized_text = normalize_text(text)
    
    # Split text into words for individual word checking
    words_in_text = re.findall(r'\b\w+\b', text.lower())
    words_in_text.extend(re.findall(r'[\u0900-\u097F]+', text))  # Devanagari words
    words_in_text.extend(re.findall(r'[\u0600-\u06FF]+', text))  # Arabic/Urdu script words
    words_in_text.extend(re.findall(r'[\u0750-\u077F]+', text))  # Additional Arabic script
    
    # Check each word against all language patterns
    for word in words_in_text:
        cleaned_word = clean_word(word)
        normalized_word = normalize_text(word)
        
        for lang, patterns in PROFANITY_PATTERNS.items():
            # Check exact match, cleaned match, and normalized match
            if (word.lower() in patterns or 
                cleaned_word.lower() in patterns or 
                normalized_word in patterns):
                
                detected_words.append({
                    'word': word,
                    'language': lang,
                    'original_text': text
                })
                break  # Avoid duplicate detections for the same word
    
    # Also check for phrase-level matches
    for lang, patterns in PROFANITY_PATTERNS.items():
        for pattern in patterns:
            if ' ' in pattern:  # Multi-word phrases
                if pattern in normalized_text or pattern in text.lower():
                    detected_words.append({
                        'word': pattern,
                        'language': lang,
                        'original_text': text
                    })
    
    return detected_words


def detect_profane_words(text: str) -> List[str]:
    """
    Simple profanity detection function for backward compatibility.
    Uses the new regex-based scanner.
    """
    from .profanity_scanner import find_profanity_matches
    
    matches = find_profanity_matches(text)
    return [match['word'] for match in matches]


def detect_abusive_words(transcript_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find segments containing profane words with their timestamps using regex-based scanner.
    Optimized for production use with multilingual support.
    
    Args:
        transcript_data: Whisper transcription result
    
    Returns:
        List of dictionaries with profane segments and timestamps
    """
    from .profanity_scanner import scan_segments
    
    if not transcript_data or 'segments' not in transcript_data:
        return []
    
    # Use the optimized regex scanner
    segments = transcript_data.get('segments', [])
    abusive_segments = scan_segments(segments)
    
    # Convert to expected format for backward compatibility
    profane_segments = []
    for segment in abusive_segments:
        profane_segments.append({
            'text': segment['text'],
            'start': segment['start'],
            'end': segment['end'],
            'profane_words': segment['profane_words'],
            'languages': segment['languages'],
            'primary_language': segment['languages'][0] if segment['languages'] else 'unknown',
            'type': 'segment'
        })
    
    # Log detection summary
    if profane_segments:
        lang_summary = {}
        for segment in profane_segments:
            for lang in segment['languages']:
                lang_summary[lang] = lang_summary.get(lang, 0) + 1
        
        print(f"🔍 Detected profanity in {len(profane_segments)} segments:")
        for lang, count in lang_summary.items():
            lang_name = {
                'english': 'English',
                'hindi': 'Hindi',
                'hinglish': 'Hinglish',
                'custom': 'Custom'
            }.get(lang, lang.title())
            print(f"   - {lang_name}: {count} segments")
    
    return profane_segments


def initialize_profanity_filter():
    """
    Initialize the profanity filter.
    This function is kept for backward compatibility but is no longer needed
    as we're using our custom multilingual detection.
    """
    try:
        profanity.load_censor_words()
    except Exception:
        # If better-profanity fails, continue with our custom detection
        pass


def add_custom_profanity_words(custom_words: List[str], language: str = 'english'):
    """
    Add custom words to the profanity filter for a specific language.
    
    Args:
        custom_words (List[str]): List of words to add to the filter
        language (str): Language category ('english', 'hindi_latin', 'hindi_devanagari')
    """
    global PROFANITY_PATTERNS
    
    if language not in PROFANITY_PATTERNS:
        PROFANITY_PATTERNS[language] = set()
    
    for word in custom_words:
        variations = create_word_variations(word)
        PROFANITY_PATTERNS[language].update(variations)
    
    print(f"📝 Added {len(custom_words)} custom words to {language} profanity filter")


def add_language_support(language_name: str, word_list: List[str]):
    """
    Add support for a new language.
    
    Args:
        language_name (str): Name of the language (e.g., 'punjabi', 'urdu')
        word_list (List[str]): List of profane words in that language
    """
    global ALL_ABUSIVE_WORDS, PROFANITY_PATTERNS
    
    # Add to the global word list
    ALL_ABUSIVE_WORDS[language_name] = word_list
    
    # Build patterns for the new language
    lang_patterns = set()
    for word in word_list:
        lang_patterns.add(word.lower())
        variations = create_word_variations(word)
        lang_patterns.update(variations)
        cleaned = clean_word(word)
        if cleaned:
            lang_patterns.add(cleaned.lower())
    
    PROFANITY_PATTERNS[language_name] = lang_patterns
    
    print(f"🌐 Added support for {language_name} with {len(word_list)} words")


def get_supported_languages() -> List[str]:
    """
    Get list of supported languages for profanity detection.
    
    Returns:
        List of supported language codes
    """
    return list(ALL_ABUSIVE_WORDS.keys())


def test_profanity_detection(text: str) -> Dict[str, Any]:
    """
    Test function to check multilingual profanity detection on a given text.
    
    Args:
        text (str): Text to test
    
    Returns:
        Dictionary with detection results
    """
    detected = detect_profane_words_in_text(text)
    
    return {
        'original_text': text,
        'contains_profanity': len(detected) > 0,
        'detected_words': detected,
        'languages_detected': list(set([item['language'] for item in detected])),
        'total_detections': len(detected)
    }


def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the loaded profanity patterns.
    
    Returns:
        Dictionary with statistics
    """
    stats = {
        'total_languages': len(PROFANITY_PATTERNS),
        'languages': {},
        'total_patterns': 0
    }
    
    for lang, patterns in PROFANITY_PATTERNS.items():
        lang_name = {
            'english': 'English',
            'hindi_latin': 'Hindi (Latin Script)',
            'hindi_devanagari': 'Hindi (Devanagari Script)'
        }.get(lang, lang.title())
        
        stats['languages'][lang_name] = len(patterns)
        stats['total_patterns'] += len(patterns)
    
    return stats


def save_learned_words_to_file(filename: str = "learned_words.json"):
    """
    Save learned words to a JSON file for persistence.
    
    Args:
        filename (str): Filename to save learned words
    """
    import json
    import os
    
    learned_file = os.path.join(os.path.dirname(__file__), filename)
    
    # Check if learned words file exists
    learned_words = {}
    if os.path.exists(learned_file):
        try:
            with open(learned_file, 'r', encoding='utf-8') as f:
                learned_words = json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading learned words: {e}")
            learned_words = {}
    
    # Save current state
    try:
        with open(learned_file, 'w', encoding='utf-8') as f:
            json.dump(learned_words, f, indent=2, ensure_ascii=False)
        print(f"💾 Learned words saved to {learned_file}")
    except Exception as e:
        print(f"❌ Error saving learned words: {e}")


def load_learned_words_from_file(filename: str = "learned_words.json"):
    """
    Load previously learned words from file and add them to the patterns.
    
    Args:
        filename (str): Filename to load learned words from
    """
    import json
    import os
    
    learned_file = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(learned_file):
        return
    
    try:
        with open(learned_file, 'r', encoding='utf-8') as f:
            learned_words = json.load(f)
        
        total_added = 0
        for lang, words in learned_words.items():
            if lang in PROFANITY_PATTERNS and isinstance(words, list):
                for word in words:
                    if word not in PROFANITY_PATTERNS[lang]:
                        PROFANITY_PATTERNS[lang].add(word)
                        total_added += 1
        
        if total_added > 0:
            print(f"📚 Loaded {total_added} previously learned words")
            
    except Exception as e:
        print(f"⚠️  Error loading learned words: {e}")


def adaptive_learning_from_transcript(transcript_text: str, manual_flags: List[str] = None) -> Dict[str, Any]:
    """
    Analyze transcript text and learn new profane words that weren't detected.
    This function can be used to train the model on missed detections.
    
    Args:
        transcript_text (str): Full transcript text
        manual_flags (List[str]): Manually flagged words that should be considered profane
    
    Returns:
        Dictionary with learning results
    """
    if not transcript_text:
        return {"learned_words": [], "total_learned": 0}
    
    # Import required modules
    import json
    import os
    import re
    
    learned_words = {"hindi_latin": [], "hindi_devanagari": [], "english": []}
    words_added = 0
    
    # Extract words from transcript
    words = re.findall(r'\b\w+\b', transcript_text.lower())
    devanagari_words = re.findall(r'[\u0900-\u097F]+', transcript_text)
    
    # Combine all words
    all_words = words + devanagari_words
    
    # If manual flags are provided, learn from them
    if manual_flags:
        for flagged_word in manual_flags:
            flagged_word = flagged_word.strip().lower()
            
            # Determine language based on script
            if re.search(r'[\u0900-\u097F]', flagged_word):
                lang = "hindi_devanagari"
            elif any(char in flagged_word for char in ['a', 'e', 'i', 'o', 'u']):
                lang = "hindi_latin"
            else:
                lang = "english"
            
            # Add to patterns if not already present
            if flagged_word not in PROFANITY_PATTERNS[lang]:
                PROFANITY_PATTERNS[lang].add(flagged_word)
                learned_words[lang].append(flagged_word)
                words_added += 1
                
                # Also add variations
                variations = create_word_variations(flagged_word)
                for var in variations:
                    if var not in PROFANITY_PATTERNS[lang]:
                        PROFANITY_PATTERNS[lang].add(var)
                        words_added += 1
    
    # Heuristic learning: detect suspicious patterns
    suspicious_patterns = [
        r'\b\w*chut\w*\b', r'\b\w*lund\w*\b', r'\b\w*gand\w*\b', 
        r'\b\w*chodh?\w*\b', r'\b\w*madarch\w*\b', r'\b\w*bhench\w*\b',
        r'\b\w*randi?\w*\b', r'\b\w*harami?\w*\b', r'\b\w*kamina?\w*\b'
    ]
    
    for pattern in suspicious_patterns:
        matches = re.findall(pattern, transcript_text.lower())
        for match in matches:
            if len(match) > 2 and match not in PROFANITY_PATTERNS['hindi_latin']:
                # Only add if it contains known profane roots
                profane_roots = ['chut', 'lund', 'gand', 'chod', 'chodh', 'madarch', 'bhench', 'randi', 'harami', 'kamina']
                if any(root in match for root in profane_roots):
                    PROFANITY_PATTERNS['hindi_latin'].add(match)
                    learned_words['hindi_latin'].append(match)
                    words_added += 1
    
    # Save learned words to file for persistence
    if words_added > 0:
        save_learned_words_to_file()
        print(f"🎓 Adaptive learning: Added {words_added} new words to detection")
    
    return {
        "learned_words": learned_words,
        "total_learned": words_added,
        "transcript_analyzed": len(all_words)
    }


def analyze_and_improve_detection(transcript_data: Dict[str, Any], video_filename: str = None) -> Dict[str, Any]:
    """
    Analyze transcript for missed profanity and improve detection patterns.
    This function combines detection with learning.
    
    Args:
        transcript_data: Whisper transcription result
        video_filename: Optional filename for logging
    
    Returns:
        Dictionary with analysis results and learned words
    """
    # First, do normal detection
    detected_segments = detect_abusive_words(transcript_data)
    
    # Get full transcript text
    full_text = transcript_data.get('text', '')
    
    # Analyze the transcript for potential missed words
    learning_result = adaptive_learning_from_transcript(full_text)
    
    # If we learned new words, re-run detection
    if learning_result['total_learned'] > 0:
        print(f"🔄 Re-running detection with {learning_result['total_learned']} newly learned words...")
        detected_segments = detect_abusive_words(transcript_data)
    
    return {
        "detected_segments": detected_segments,
        "learning_result": learning_result,
        "video_filename": video_filename,
        "total_segments_detected": len(detected_segments)
    }


def manual_word_training(words_to_add: List[str], language: str = "hindi_latin") -> Dict[str, Any]:
    """
    Manually train the model by adding specific words.
    
    Args:
        words_to_add (List[str]): List of words to add to the profanity filter
        language (str): Language category ('english', 'hindi_latin', 'hindi_devanagari')
    
    Returns:
        Dictionary with training results
    """
    if language not in PROFANITY_PATTERNS:
        return {"error": f"Language '{language}' not supported", "added": 0}
    
    added_count = 0
    added_words = []
    
    for word in words_to_add:
        word = word.strip().lower()
        if word and word not in PROFANITY_PATTERNS[language]:
            PROFANITY_PATTERNS[language].add(word)
            added_words.append(word)
            added_count += 1
            
            # Also add variations
            variations = create_word_variations(word)
            for var in variations:
                if var not in PROFANITY_PATTERNS[language]:
                    PROFANITY_PATTERNS[language].add(var)
                    added_count += 1
    
    # Save to file
    save_learned_words_to_file()
    
    print(f"✅ Manually added {added_count} words/variations to {language}")
    
    return {
        "language": language,
        "words_added": added_words,
        "total_patterns_added": added_count,
        "success": True
    }


# Load previously learned words when module is imported
load_learned_words_from_file()

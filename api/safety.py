"""Local safety net: defer risky questions before any LLM call."""


EMERGENCY = "emergency"
HARM = "harm"
HEALTH = "health"

EMERGENCY_MARKERS = (
    "kill myself", "suicide", "want to die", "hurt myself", "overdose",
    "poison", "heart attack", "can't breathe", "cannot breathe", "heavy bleeding",
    "bleeding heavily", "emergency", "ambulance", "fire!", "there is a fire",
)
HARM_MARKERS = (
    "make a bomb", "build a bomb", "make poison", "how to steal", "how to hack",
    "hack into", "break into", "make a weapon", "buy a gun", "buy drugs",
    "sell drugs", "how to kidnap",
)
HEALTH_MARKERS = (
    "fever", "malaria", "medicine", "medication", "antibiotic", "doctor",
    "hospital", "clinic", "pregnant", "pregnancy", "diarrhea", "diarrhoea",
    "vaccine", "vaccination", "sick", "headache", "stomach ache", "cough",
    "rash", "blood pressure", "hiv", "aids", "cholera", "typhoid",
    "sore throat", "health problem", "health question", "i am ill", "i'm ill",
    "homa", "mgonjwa", "dawa", "daktari", "hospitali", "mimba",
    "ugonjwa", "umguli", "udokotela", "imithi", "marazi", "asibiti",
    "malade", "médecin", "medecin", "médicament", "medicament", "hôpital",
    "hopital", "fièvre", "fievre",
)

DEFER_REPLIES = {
    "en": {
        HEALTH: "I'm not a doctor. Please talk to a local health professional or clinic about this.",
        EMERGENCY: "I can't handle an emergency. Please contact local emergency services now.",
        HARM: "I can't help with that. Please talk to a qualified local professional instead.",
    },
    "sw": {
        HEALTH: "Si daktari. Tafadhali zungumza na mtaalamu wa afya au kliniki ya karibu.",
        EMERGENCY: "Siwezi kushughulikia dharura. Tafadhali wasiliana na huduma za dharura sasa.",
        HARM: "Siwezi kusaidia na hilo. Tafadhali zungumza na mtaalamu aliyehitimu.",
    },
    "zu": {
        HEALTH: "Angisiye udokotela. Sicela ukhulume nodokotela noma emtholampilo wendawo.",
        EMERGENCY: "Angikwazi ukusingatha izimo eziphuthumayo. Shayela izinsizakalo eziphuthumayo manje.",
        HARM: "Angikwazi ukusiza ngalokho. Sicela ukhulume nochwepheshe ofanelekile.",
    },
    "xh": {
        HEALTH: "Andilogqirha. Nceda uthethe nogqirha okanye kwikliniki yasekuhlaleni.",
        EMERGENCY: "Andinakujongana neemeko zikaxakeka. Qhagamshelana neenkonzo zikaxakeka ngoku.",
        HARM: "Andinakukunceda ngaloo nto. Nceda uthethe nengcali efanelekileyo.",
    },
    "af": {
        HEALTH: "Ek is nie 'n dokter nie. Praat asseblief met 'n plaaslike gesondheidswerker of kliniek.",
        EMERGENCY: "Ek kan nie 'n noodgeval hanteer nie. Kontak asseblief nou plaaslike nooddienste.",
        HARM: "Ek kan nie hiermee help nie. Praat asseblief met 'n gekwalifiseerde professionele persoon.",
    },
    "am": {
        HEALTH: "እኔ ዶክተር አይደለሁም። እባክዎ ከአካባቢዎ የጤና ባለሙያ ወይም ከክሊኒክ ጋር ይነጋገሩ።",
        EMERGENCY: "ድንገተኛ ሁኔታን ማስተናገድ አልችልም። እባክዎ አሁን የድንገተኛ አገልግሎት ያግኙ።",
        HARM: "በዚህ ልርድ አልችልም። እባክዎ ብቁ ከሆነ የአካባቢ ባለሙያ ጋር ይነጋገሩ።",
    },
    "yo": {
        HEALTH: "Emi kii ṣe dokita. Jọwọ ba oníṣègùn agbegbe tabi ile-iwosan sọrọ.",
        EMERGENCY: "Emi ko le mu ọrọ pajawiri. Jọwọ pe awọn iṣẹ pajawiri agbegbe lọwọlọwọ.",
        HARM: "Emi ko le ran yẹn lọwọ. Jọwọ ba akíkanjú agbegbe sọrọ.",
    },
    "ha": {
        HEALTH: "Ba ni likita ba. Da fatan za ku tattauna da likitan gida ko asibitin da ke kusa.",
        EMERGENCY: "Ba zan iya kula da gaggawa ba. Da fatan za ku tuntubi sabis na gaggawa yanzu.",
        HARM: "Ba zan iya taimakawa da hakan ba. Da fatan za ku tattauna da kwararren mutum na gida.",
    },
    "ig": {
        HEALTH: "Abụghị m dọkịta. Biko kpụtara onye ọkachamara ahụike ma ọ bụ ụlọ ọgwụ dị nso.",
        EMERGENCY: "Enweghị m ike ijikwa ihe mberede. Biko kpọtụrụ ọrụ mberede ugbu a.",
        HARM: "Enweghị m ike inye aka na nke a. Biko gwa onye ọkachamara ruru eru.",
    },
    "rw": {
        HEALTH: "Si muganga. Nyamuneka uvugane n'umuganga w'aho utuye cyangwa ikigo nderabuzima.",
        EMERGENCY: "Sinshobora kwita ku byihutirwa. Hamagara serivisi z'ubutabazi z'aho utuye nonaha.",
        HARM: "Sinshobora kukufasha kuri ibyo. Nyamuneka uvugane n'inzobere ibifite uruhare.",
    },
    "so": {
        HEALTH: "Ma ihi dhakhtar. Fadlan kala hadal xirfadle caafimaad oo deegaanka ah ama rug caafimaad.",
        EMERGENCY: "Ma maareyn karo xaalad degdeg ah. Fadlan hadda la xiriir adeegyada degdegga ah.",
        HARM: "Ma kaa caawin karo arrintan. Fadlan la hadal xirfadle u qalma.",
    },
    "fr": {
        HEALTH: "Je ne suis pas médecin. Veuillez consulter un professionnel de santé ou un centre de santé local.",
        EMERGENCY: "Je ne peux pas gérer une urgence. Contactez les services d'urgence locaux maintenant.",
        HARM: "Je ne peux pas aider avec cela. Veuillez consulter un professionnel qualifié.",
    },
}

FALLBACK = DEFER_REPLIES["en"]


def _contains(text, markers):
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def check(text):
    if not isinstance(text, str) or not text.strip():
        return None
    if _contains(text, EMERGENCY_MARKERS):
        return EMERGENCY
    if _contains(text, HARM_MARKERS):
        return HARM
    if _contains(text, HEALTH_MARKERS):
        return HEALTH
    return None


def deferral(lang, category):
    base = ""
    if isinstance(lang, str):
        base = lang.strip().lower().replace("_", "-").split("-")[0]
    replies = DEFER_REPLIES.get(base, FALLBACK)
    return replies.get(category, FALLBACK[category])

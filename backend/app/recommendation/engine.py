"""Disease knowledge base and recommendation engine for pomegranate crops."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DiseaseInfo:
    """Structured disease metadata used for diagnosis and reporting."""

    name: str
    affected_part: str
    description: str
    possible_causes: List[str]
    environmental_conditions: List[str]
    severity_indicators: Dict[str, str]


@dataclass
class Recommendation:
    """Treatment and agronomic recommendations for a detected disease."""

    fertilizer: str
    npk_ratio: str
    micronutrients: List[str]
    organic_fertilizer: str
    bio_fertilizer: str
    fungicide: Optional[str]
    pesticide: Optional[str]
    dosage: str
    spraying_interval: str
    safety_precautions: List[str]
    recovery_time: str
    preventive_measures: List[str]
    irrigation: str
    farming_practice: str
    organic_treatment: List[str] = field(default_factory=list)


DISEASE_KNOWLEDGE: Dict[str, DiseaseInfo] = {
    "Healthy": DiseaseInfo(
        name="Healthy",
        affected_part="Fruit / Leaf",
        description=(
            "The pomegranate plant shows no visible signs of disease or nutrient stress. "
            "Leaves are green and firm; fruits are uniformly colored without lesions."
        ),
        possible_causes=["Balanced nutrition", "Proper irrigation", "Good orchard hygiene"],
        environmental_conditions=["Moderate humidity", "Adequate sunlight", "Well-drained soil"],
        severity_indicators={"mild": "N/A", "moderate": "N/A", "severe": "N/A"},
    ),
    "Bacterial Blight": DiseaseInfo(
        name="Bacterial Blight",
        affected_part="Leaf / Stem / Fruit",
        description=(
            "Water-soaked lesions that turn dark brown to black. Affected tissues may "
            "exhibit angular spots with yellow halos and premature leaf drop."
        ),
        possible_causes=[
            "Xanthomonas axonopodis pv. punicae",
            "Wound entry from pruning or hail",
            "Overhead irrigation splashing bacteria",
        ],
        environmental_conditions=[
            "High humidity above 85%",
            "Warm temperatures 25-35°C",
            "Prolonged leaf wetness",
        ],
        severity_indicators={
            "mild": "Few scattered lesions on lower canopy",
            "moderate": "Multiple branches affected, 10-30% defoliation",
            "severe": "Extensive blight, >30% canopy loss, fruit cracking",
        },
    ),
    "Anthracnose": DiseaseInfo(
        name="Anthracnose",
        affected_part="Fruit / Leaf",
        description=(
            "Sunken circular lesions with dark margins on fruits and leaves. "
            "In humid conditions lesions may produce pinkish spore masses."
        ),
        possible_causes=["Colletotrichum spp.", "Infected planting material", "Rain splash dispersal"],
        environmental_conditions=["Rainy season", "High humidity", "Poor air circulation"],
        severity_indicators={
            "mild": "Small isolated spots on few fruits",
            "moderate": "Multiple fruits with coalescing lesions",
            "severe": "Fruit rot and significant marketability loss",
        },
    ),
    "Cercospora Fruit Spot": DiseaseInfo(
        name="Cercospora Fruit Spot",
        affected_part="Fruit / Leaf",
        description=(
            "Small circular brown spots with ash-gray centers on fruits and foliage. "
            "Spots may enlarge and merge under favorable conditions."
        ),
        possible_causes=["Cercospora spp.", "Dense planting", "Residual inoculum on debris"],
        environmental_conditions=["Moderate to high humidity", "Warm nights", "Shaded canopy"],
        severity_indicators={
            "mild": "Scattered spots covering <5% fruit surface",
            "moderate": "5-20% fruit surface affected",
            "severe": ">20% fruit affected, premature drop",
        },
    ),
    "Alternaria": DiseaseInfo(
        name="Alternaria",
        affected_part="Fruit / Leaf",
        description=(
            "Dark brown to black concentric rings on leaves and fruits. "
            "Alternaria rot causes soft decay during storage."
        ),
        possible_causes=["Alternaria alternata", "Mechanical injury", "Nutrient imbalance"],
        environmental_conditions=["Alternating wet-dry cycles", "Post-harvest moisture", "Wounds on fruit"],
        severity_indicators={
            "mild": "Few leaf spots, minimal fruit damage",
            "moderate": "Leaf blight and early fruit rot",
            "severe": "Storage rot epidemic, major yield loss",
        },
    ),
    "Wilt Disease": DiseaseInfo(
        name="Wilt Disease",
        affected_part="Root / Stem / Leaf",
        description=(
            "Progressive wilting despite adequate soil moisture. Leaves yellow and droop; "
            "vascular discoloration may be visible when stems are cut."
        ),
        possible_causes=[
            "Fusarium oxysporum or Verticillium spp.",
            "Waterlogged soil",
            "Root damage from nematodes",
        ],
        environmental_conditions=["Heavy clay soils", "Poor drainage", "Soil temperature 25-30°C"],
        severity_indicators={
            "mild": "Single branch wilting",
            "moderate": "Partial canopy wilt, stunted growth",
            "severe": "Whole plant collapse and death",
        },
    ),
    "Leaf Spot": DiseaseInfo(
        name="Leaf Spot",
        affected_part="Leaf",
        description=(
            "Circular to irregular brown or purple spots on leaves. Severe infections "
            "cause defoliation and reduced photosynthesis."
        ),
        possible_causes=["Various fungal pathogens", "Nutrient deficiency stress", "Overhead irrigation"],
        environmental_conditions=["Leaf wetness >12 hours", "Moderate temperatures", "Dense foliage"],
        severity_indicators={
            "mild": "<10% leaf area affected",
            "moderate": "10-30% leaf area affected",
            "severe": ">30% defoliation",
        },
    ),
    "Fruit Rot": DiseaseInfo(
        name="Fruit Rot",
        affected_part="Fruit",
        description=(
            "Soft, watery decay of pomegranate arils and rind. May spread rapidly "
            "during storage or after rain damage."
        ),
        possible_causes=["Botrytis cinerea", "Penicillium spp.", "Insect wounds", "Cracked fruit"],
        environmental_conditions=["High humidity in storage", "Rain before harvest", "Warm temperatures"],
        severity_indicators={
            "mild": "Localized rot on few fruits",
            "moderate": "Multiple fruits with spreading decay",
            "severe": "Field or storage epidemic",
        },
    ),
    "Nutrient Deficiency": DiseaseInfo(
        name="Nutrient Deficiency",
        affected_part="Leaf / Fruit",
        description=(
            "Chlorosis, interveinal yellowing, stunted growth, or poor fruit set indicating "
            "insufficient macro or micronutrients."
        ),
        possible_causes=[
            "Imbalanced fertilization",
            "Alkaline soil locking micronutrients",
            "Root dysfunction limiting uptake",
        ],
        environmental_conditions=["Calcareous soils", "Excessive irrigation leaching", "Low organic matter"],
        severity_indicators={
            "mild": "Early chlorosis on young leaves",
            "moderate": "Widespread discoloration, reduced fruit size",
            "severe": "Severe stunting, flower/fruit drop",
        },
    ),
}


RECOMMENDATIONS: Dict[str, Recommendation] = {
    "Healthy": Recommendation(
        fertilizer="Balanced NPK maintenance fertilizer",
        npk_ratio="10-10-10 or 14-14-14",
        micronutrients=["Zinc", "Boron", "Iron"],
        organic_fertilizer="Compost 5-10 kg per tree annually",
        bio_fertilizer="Azotobacter + PSB consortia",
        fungicide=None,
        pesticide=None,
        dosage="500 g NPK per mature tree per split application",
        spraying_interval="Foliar micronutrients every 30-45 days if needed",
        safety_precautions=["Follow label rates", "Avoid application during peak heat"],
        recovery_time="Maintenance — no recovery needed",
        preventive_measures=[
            "Monitor weekly for early symptoms",
            "Maintain mulch and weed-free basins",
            "Prune for airflow",
        ],
        irrigation="Drip irrigation 40-60 L/tree/day in fruiting stage; avoid waterlogging",
        farming_practice="Integrated nutrient management with soil testing every season",
        organic_treatment=["Neem cake soil application", "Vermicompost mulching"],
    ),
    "Bacterial Blight": Recommendation(
        fertilizer="Low-nitrogen potassium-rich fertilizer to harden tissue",
        npk_ratio="5-10-20 with calcium supplement",
        micronutrients=["Copper", "Zinc", "Boron"],
        organic_fertilizer="Trichoderma-enriched compost",
        bio_fertilizer="Pseudomonas fluorescens seedling dip",
        fungicide=None,
        pesticide="Copper oxychloride 50% WP",
        dosage="3 g/L foliar spray; repeat after 10 days",
        spraying_interval="Every 10-14 days during humid periods",
        safety_precautions=[
            "Use gloves and mask",
            "Do not tank-mix with alkaline products",
            "Observe pre-harvest interval",
        ],
        recovery_time="4-6 weeks with sanitation and copper program",
        preventive_measures=[
            "Use disease-free planting material",
            "Avoid overhead irrigation",
            "Disinfect pruning tools",
        ],
        irrigation="Switch to drip; irrigate early morning; keep canopy dry",
        farming_practice="Remove and burn infected debris; improve row spacing",
        organic_treatment=[
            "Neem oil 3 mL/L spray",
            "Garlic-chilli extract foliar application",
            "Bordeaux mixture 1% as protective spray",
        ],
    ),
    "Anthracnose": Recommendation(
        fertilizer="Balanced NPK with extra potassium",
        npk_ratio="8-12-20",
        micronutrients=["Boron", "Zinc"],
        organic_fertilizer="Well-decomposed FYM 20 kg/tree",
        bio_fertilizer="Trichoderma harzianum soil drench",
        fungicide="Mancozeb 75% WP or Azoxystrobin 23% SC",
        pesticide=None,
        dosage="2.5 g/L Mancozeb or 1 mL/L Azoxystrobin",
        spraying_interval="Every 12-15 days until dry weather",
        safety_precautions=["Rotate fungicide groups", "Use PPE during spraying"],
        recovery_time="3-5 weeks depending on fruit load",
        preventive_measures=["Sanitation", "Harvest at proper maturity", "Post-harvest fungicide dip"],
        irrigation="Reduce leaf wetness duration; use micro-sprinklers carefully",
        farming_practice="Open canopy pruning; remove mummified fruits",
        organic_treatment=["Neem oil + baking soda spray", "Compost tea foliar feed"],
    ),
    "Cercospora Fruit Spot": Recommendation(
        fertilizer="Moderate nitrogen with potassium and calcium",
        npk_ratio="10-8-18",
        micronutrients=["Magnesium", "Manganese"],
        organic_fertilizer="Green manure intercrop",
        bio_fertilizer="Trichoderma + Bacillus subtilis",
        fungicide="Carbendazim 50% WP or Chlorothalonil 75% WP",
        pesticide=None,
        dosage="1 g/L Carbendazim or 2 g/L Chlorothalonil",
        spraying_interval="Every 15 days",
        safety_precautions=["Avoid drift to water bodies", "Rotate active ingredients"],
        recovery_time="2-4 weeks",
        preventive_measures=["Remove leaf litter", "Balanced fertilization"],
        irrigation="Morning irrigation only; maintain soil moisture not saturation",
        farming_practice="Reflective mulches to reduce humidity in canopy",
        organic_treatment=["Sulfur dust 2-3 kg/acre", "Neem-based botanical fungicide"],
    ),
    "Alternaria": Recommendation(
        fertilizer="Potassium-forward fertilizer after flowering",
        npk_ratio="6-10-24",
        micronutrients=["Zinc", "Copper"],
        organic_fertilizer="Compost + biochar blend",
        bio_fertilizer="Trichoderma seedling treatment",
        fungicide="Difenoconazole 25% EC or Iprodione 50% WP",
        pesticide=None,
        dosage="1 mL/L Difenoconazole",
        spraying_interval="Every 10-14 days pre-harvest",
        safety_precautions=["Observe PHI", "Do not exceed label rates"],
        recovery_time="3-4 weeks",
        preventive_measures=["Minimize fruit injury", "Cool storage", "Sanitize bins"],
        irrigation="Avoid wetting fruit during irrigation",
        farming_practice="Harvest promptly; cull wounded fruit",
        organic_treatment=["Neem oil 5 mL/L", "Potassium bicarbonate spray"],
    ),
    "Wilt Disease": Recommendation(
        fertilizer="Phosphorus and potassium boost; avoid excess nitrogen",
        npk_ratio="5-15-20",
        micronutrients=["Silicon", "Zinc"],
        organic_fertilizer="Neem cake + compost soil incorporation",
        bio_fertilizer="Trichoderma + Pseudomonas root drench",
        fungicide="Carbendazim soil drench or Propiconazole trunk injection (expert supervision)",
        pesticide=None,
        dosage="1 g/L soil drench 5 L per tree",
        spraying_interval="Single drench + repeat after 21 days if needed",
        safety_precautions=["Improve drainage before chemical drench", "Remove dead plants"],
        recovery_time="6-10 weeks; severe cases may not recover",
        preventive_measures=["Use resistant rootstocks", "Solarization", "Crop rotation where possible"],
        irrigation="Strict deficit avoidance but prevent waterlogging",
        farming_practice="Rogue out infected plants; disinfect tools with bleach",
        organic_treatment=["Trichoderma 10 g/L drench", "Mustard cake soil amendment"],
    ),
    "Leaf Spot": Recommendation(
        fertilizer="Balanced NPK with micronutrient foliar",
        npk_ratio="12-12-17",
        micronutrients=["Iron", "Manganese", "Zinc"],
        organic_fertilizer="Vermicompost foliar extract",
        bio_fertilizer="Bacillus subtilis foliar spray",
        fungicide="Copper hydroxide 77% WP",
        pesticide=None,
        dosage="2.5 g/L",
        spraying_interval="Every 14 days",
        safety_precautions=["Copper phytotoxicity on young leaves — test small area"],
        recovery_time="2-3 weeks",
        preventive_measures=["Prune lower infected leaves", "Improve airflow"],
        irrigation="Drip preferred; reduce duration of leaf wetness",
        farming_practice="Mulching to prevent soil splash",
        organic_treatment=["Neem oil", "Milk spray 1:9 with water"],
    ),
    "Fruit Rot": Recommendation(
        fertilizer="Calcium and potassium supplement to strengthen rind",
        npk_ratio="8-8-20 + Ca",
        micronutrients=["Boron", "Calcium"],
        organic_fertilizer="Compost mulch around basin",
        bio_fertilizer="Trichoderma pre-harvest soil application",
        fungicide="Fludioxonil or Pyraclostrobin (follow local labels)",
        pesticide=None,
        dosage="As per product label for pomegranate",
        spraying_interval="Pre-harvest protective sprays every 10 days",
        safety_precautions=["Strict PHI compliance", "Store fungicides securely"],
        recovery_time="2-4 weeks for field rot; storage losses immediate",
        preventive_measures=["Harvest dry fruit", "Sanitize packing house", "Rapid cooling"],
        irrigation="Stop overhead irrigation 2 weeks before harvest",
        farming_practice="Field sanitation; remove rotted fruit promptly",
        organic_treatment=["Neem oil pre-harvest spray", "Hot water fruit treatment 52°C 2 min"],
    ),
    "Nutrient Deficiency": Recommendation(
        fertilizer="Targeted correction based on soil test",
        npk_ratio="Variable — e.g. 20-10-10 for N deficiency; 0-0-50 for K deficiency",
        micronutrients=["Fe-EDDHA", "ZnSO4", "Boric acid as needed"],
        organic_fertilizer="Compost + rock phosphate + wood ash blend",
        bio_fertilizer="Azotobacter, PSB, KMB consortia",
        fungicide=None,
        pesticide=None,
        dosage="Foliar: 2-5 g/L micronutrient chelates; soil per soil test",
        spraying_interval="Micronutrient foliar every 15-21 days until recovery",
        safety_precautions=["Do not over-apply boron", "Split nitrogen applications"],
        recovery_time="3-6 weeks for visible green-up",
        preventive_measures=["Annual soil and leaf analysis", "Maintain pH 6.0-7.5"],
        irrigation="Fertigation via drip for efficient uptake",
        farming_practice="Organic matter incorporation; balanced split fertilization",
        organic_treatment=["Seaweed extract foliar", "Compost tea", "Green manure"],
    ),
}


def compute_severity(confidence: float, disease_name: str) -> str:
    """Map model confidence to agronomic severity for diseased classes."""
    if disease_name == "Healthy":
        return "None"

    if confidence >= 0.85:
        return "Severe"
    if confidence >= 0.65:
        return "Moderate"
    return "Mild"


# Map checkpoint class labels (underscored) onto knowledge-base keys
CLASS_ALIASES = {
    "Bacterial_Blight": "Bacterial Blight",
    "Cercospora": "Cercospora Fruit Spot",
    "Alternaria": "Alternaria",
    "Anthracnose": "Anthracnose",
    "Healthy": "Healthy",
}


def normalize_disease_name(disease_name: str) -> str:
    return CLASS_ALIASES.get(disease_name, disease_name)


def get_disease_info(disease_name: str) -> DiseaseInfo:
    key = normalize_disease_name(disease_name)
    return DISEASE_KNOWLEDGE.get(key, DISEASE_KNOWLEDGE["Healthy"])


def get_recommendation(disease_name: str) -> Recommendation:
    key = normalize_disease_name(disease_name)
    return RECOMMENDATIONS.get(key, RECOMMENDATIONS["Healthy"])


def build_diagnosis_payload(disease_name: str, confidence: float) -> Dict[str, Any]:
    """Assemble full diagnosis dictionary for API responses and PDF reports."""
    info = get_disease_info(disease_name)
    rec = get_recommendation(disease_name)
    canonical = normalize_disease_name(disease_name)
    severity = compute_severity(confidence, canonical)

    return {
        "disease_name": disease_name,
        "display_name": canonical,
        "confidence": round(confidence * 100, 2),
        "affected_part": info.affected_part,
        "severity": severity,
        "description": info.description,
        "possible_causes": info.possible_causes,
        "environmental_conditions": info.environmental_conditions,
        "severity_detail": info.severity_indicators.get(severity.lower(), "See field assessment"),
        "recommendations": {
            "fertilizer": rec.fertilizer,
            "npk_ratio": rec.npk_ratio,
            "micronutrients": rec.micronutrients,
            "organic_fertilizer": rec.organic_fertilizer,
            "bio_fertilizer": rec.bio_fertilizer,
            "fungicide": rec.fungicide,
            "pesticide": rec.pesticide,
            "dosage": rec.dosage,
            "spraying_interval": rec.spraying_interval,
            "safety_precautions": rec.safety_precautions,
            "recovery_time": rec.recovery_time,
            "preventive_measures": rec.preventive_measures,
            "irrigation": rec.irrigation,
            "farming_practice": rec.farming_practice,
            "organic_treatment": rec.organic_treatment,
        },
    }

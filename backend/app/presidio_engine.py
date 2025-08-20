from __future__ import annotations

from functools import lru_cache
from typing import Dict, List


@lru_cache(maxsize=1)
def _get_analyzer():
	# Lazy imports to keep startup light
	from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
	from presidio_analyzer.nlp_engine import NlpEngineProvider

	nlp_engine = None
	try:
		# Prefer medium model; fall back to small
		provider = NlpEngineProvider(nlp_configuration={
			"nlp_engine_name": "spacy",
			"models": [
				{"lang_code": "en", "model_name": "en_core_web_md"},
			],
		})
		nlp_engine = provider.create_engine()
	except Exception:
		try:
			provider = NlpEngineProvider(nlp_configuration={
				"nlp_engine_name": "spacy",
				"models": [
					{"lang_code": "en", "model_name": "en_core_web_sm"},
				],
			})
			nlp_engine = provider.create_engine()
		except Exception:
			# Final fallback: regex-only engine (no spaCy). Built-in regex recognizers still work.
			nlp_engine = None

	analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])  # type: ignore

	# Add custom Aadhaar recognizer
	aadhaar_pattern = Pattern(
		name="aadhaar_number",
		regex=r"\b(?:\d{4}\s?\d{4}\s?\d{4})\b",
		score=0.7,
	)
	aadhaar_recognizer = PatternRecognizer(
		patterns=[aadhaar_pattern],
		context=["aadhaar", "uidai", "uid", "govt", "government"],
		supported_entity="AADHAAR_NUMBER",
	)
	analyzer.registry.add_recognizer(aadhaar_recognizer)
	return analyzer


ENTITY_MAP = {
	"PERSON": "PERSON",
	"EMAIL_ADDRESS": "EMAIL_ADDRESS",
	"PHONE_NUMBER": "PHONE_NUMBER",
	"US_SSN": "US_SSN",
	"LOCATION": "ADDRESS",
	"AADHAAR_NUMBER": "AADHAAR_NUMBER",
}


def analyze_texts(texts: List[str]) -> List[List[Dict]]:
	"""
	Analyze a list of text snippets; return list aligned with input, where each item is
	a list of dicts: {"entity_type": str, "score": float, "start": int, "end": int}.
	"""
	analyzer = _get_analyzer()
	results: List[List[Dict]] = []
	for t in texts:
		if not t:
			results.append([])
			continue
		res = analyzer.analyze(text=t, language="en")
		entities = []
		for r in res:
			label = ENTITY_MAP.get(r.entity_type, r.entity_type)
			entities.append({
				"entity_type": label,
				"score": float(r.score),
				"start": int(r.start),
				"end": int(r.end),
			})
		results.append(entities)
	return results 
"""
Canonical Darwin Core field map for the Protista catalogue.

One ordered source of truth, shared by the model, the ingest column mapping and
the DwC-A / CSV export. Columns mirror the CTFB extended spreadsheet
(`mv_planilha_extendida.csv`), plus the two protist additions (`supergroup`,
`clade_id`).

Each entry: (csv_header, model_attr, term_uri)

Standard Darwin Core / Dublin Core terms use their official URIs; CTFB-specific
or non-standard ranks use the project namespace below so the DwC-A meta.xml is
still well-formed.
"""

DWC = "http://rs.tdwg.org/dwc/terms/"
DC = "http://purl.org/dc/terms/"
NS = "http://catalogo-protista.org/terms/"   # project namespace for custom terms

# Ordered: taxonID first (DwC-A core id), then the rest.
TERMS = [
    ("taxonID",                   "taxon_id",                    DWC + "taxonID"),
    # protist additions
    ("supergroup",                "supergroup",                  DWC + "kingdom"),
    ("clade",                     "clade_id",                    NS + "clade"),
    # names
    ("scientificName",            "scientific_name",             DWC + "scientificName"),
    ("taxonRank",                 "taxon_rank",                  DWC + "taxonRank"),
    ("parentNameUsage",           "parent_name_usage",           DWC + "parentNameUsage"),
    ("parentNameUsageID",         "parent_name_usage_id",        DWC + "parentNameUsageID"),
    ("higherClassification",      "higher_classification",       DWC + "higherClassification"),
    # ranks
    ("phylum",                    "phylum",                      DWC + "phylum"),
    ("superClass",                "super_class",                 NS + "superClass"),
    ("class",                     "class_",                      DWC + "class"),
    ("subClass",                  "sub_class",                   NS + "subClass"),
    ("infraClass",                "infra_class",                 NS + "infraClass"),
    ("superOrder",                "super_order",                 NS + "superOrder"),
    ("order",                     "order",                       DWC + "order"),
    ("subOrder",                  "sub_order",                   NS + "subOrder"),
    ("infraOrder",                "infra_order",                 NS + "infraOrder"),
    ("superFamily",               "super_family",                NS + "superFamily"),
    ("family",                    "family",                      DWC + "family"),
    ("subFamily",                 "sub_family",                  NS + "subFamily"),
    ("tribe",                     "tribe",                       NS + "tribe"),
    ("subTribe",                  "sub_tribe",                   NS + "subTribe"),
    ("genus",                     "genus",                       DWC + "genus"),
    ("subGenus",                  "subgenus",                    DWC + "subgenus"),
    ("specificEpithet",           "specific_epithet",            DWC + "specificEpithet"),
    ("infraspecificEpithet",      "infraspecific_epithet",       DWC + "infraspecificEpithet"),
    ("scientificNameAuthorship",  "scientific_name_authorship",  DWC + "scientificNameAuthorship"),
    ("namePublishedInYear",       "name_published_in_year",      DWC + "namePublishedInYear"),
    # status
    ("taxonomicStatus",           "taxonomic_status",            DWC + "taxonomicStatus"),
    ("acceptedNameUsage",         "accepted_name_usage",         DWC + "acceptedNameUsage"),
    ("acceptedNameUsageID",       "accepted_name_usage_id",      DWC + "acceptedNameUsageID"),
    ("nomenclaturalStatus",       "nomenclatural_status",        DWC + "nomenclaturalStatus"),
    ("modified",                  "modified",                    DC + "modified"),
    ("bibliographicCitation",     "bibliographic_citation",      DC + "bibliographicCitation"),
    ("bibliographicReference",    "bibliographic_reference",     NS + "bibliographicReference"),
    # distribution
    ("country",                   "country",                     DWC + "country"),
    ("countryCode",               "country_code",                DWC + "countryCode"),
    ("establishmentMeans",        "establishment_means",         DWC + "establishmentMeans"),
    ("endemicBrazil",             "endemic_brazil",              NS + "endemicBrazil"),
    ("environment",               "environment",                 NS + "environment"),
    ("locationID",                "location_id",                 DWC + "locationID"),
    ("epicontinentalDomain",      "epicontinental_domain",       NS + "epicontinentalDomain"),
    ("marineDomain",              "marine_domain",               NS + "marineDomain"),
    ("lifeForm",                  "life_form",                   NS + "lifeForm"),
    ("habitat",                   "habitat",                     DWC + "habitat"),
    # vernacular
    ("vernacularName",            "vernacular_name",             DWC + "vernacularName"),
    ("vernacularNameLanguage",    "vernacular_name_language",    NS + "vernacularNameLanguage"),
    ("vernacularNameLocality",    "vernacular_name_locality",    NS + "vernacularNameLocality"),
    # hosts / symbionts
    ("animalHostIds",             "animal_host_ids",             NS + "animalHostIds"),
    ("animalHostNames",           "animal_host_names",           NS + "animalHostNames"),
    ("vegetalHostNames",          "vegetal_host_names",          NS + "vegetalHostNames"),
    ("animalSymbiontIds",         "animal_symbiont_ids",         NS + "animalSymbiontIds"),
    ("animalSymbiontNames",       "animal_symbiont_names",       NS + "animalSymbiontNames"),
    # misc / curation
    ("occurrenceRemarks",         "occurrence_remarks",          DWC + "occurrenceRemarks"),
    ("internalRemarks",           "internal_remarks",            NS + "internalRemarks"),
    ("voucher",                   "voucher",                     NS + "voucher"),
    ("controlledBibliography",    "controlled_bibliography",     NS + "controlledBibliography"),
    ("typology",                  "typology",                    NS + "typology"),
    ("datasetName",               "dataset_name",                DWC + "datasetName"),
    ("references",                "references",                  DC + "references"),
]

# attrs that map to a model column (everything except none here)
EXPORT_FIELDS = [(attr, uri) for _, attr, uri in TERMS]

# CSV / DwC header -> model attr (for ingest); includes the canonical csv name
HEADER_TO_ATTR = {csv: attr for csv, attr, _ in TERMS}
# also accept the official term's last path segment (e.g. acceptedNameUsageID)
for _csv, _attr, _uri in TERMS:
    HEADER_TO_ATTR.setdefault(_uri.rsplit("/", 1)[-1], _attr)
# common aliases
HEADER_TO_ATTR.setdefault("id", "taxon_id")
HEADER_TO_ATTR.setdefault("kingdom", "supergroup")

# all model text attrs the CSV/DwC can write (used by ingest UPDATABLE_ATTRS)
TEXT_ATTRS = [attr for _, attr, _ in TERMS] + ["clade_id"]

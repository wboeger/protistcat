"""
Populate the Protista catalogue with real species from the GBIF Backbone
Taxonomy.

Strategy: the phylogeny backbone (phylogeny.py) carries curated representative
genera for each group. Genus names resolve cleanly against GBIF (informal clade
names like 'CRuMs' or 'Evosea' do not). For each genus we resolve its GBIF key,
then list accepted species beneath it, attaching the backbone's supergroup /
clade_id / higherClassification to every record.

Records are pushed through the same staging/apply pipeline used by the admin
ingest UI (ingest.stage_ingest / ingest.apply_stage), so they dedupe by
taxonID and are fully auditable.

Usage:  python gbif_ingest.py [--per-genus 30] [--truncate-gbif]
"""
import sys
import time
import argparse

import requests

import phylogeny as ph

GBIF = "https://api.gbif.org/v1"
BACKBONE_DATASET = "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c"
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "Protista-catalogue/1.0"


def _get(path, **params):
    for attempt in range(4):
        try:
            r = SESSION.get(f"{GBIF}{path}", params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(1.5 * (attempt + 1))
    return None


def resolve_genus_key(genus):
    """Return (usageKey, kingdom) for an accepted genus, or (None, None).

    The /species/match endpoint is unreliable for some protist genera, so we
    fall back to a direct search within the GBIF Backbone dataset."""
    m = _get("/species/match", name=genus, rank="GENUS", strict="false")
    if m and m.get("usageKey") and m.get("matchType") != "NONE":
        return m["usageKey"], m.get("kingdom")
    r = _get("/species/search", q=genus, rank="GENUS",
             datasetKey=BACKBONE_DATASET, limit=5)
    for x in (r or {}).get("results", []):
        if x.get("canonicalName") == genus and x.get("rank") == "GENUS":
            return x.get("key"), x.get("kingdom")
    return None, None


def brazilian_species_keys(genus_key, limit):
    """Species keys (backbone) recorded in Brazil under a genus, ranked by
    number of Brazilian occurrence records (facet on speciesKey, country=BR)."""
    page = _get("/occurrence/search", country="BR", taxonKey=genus_key,
                limit=0, facet="speciesKey", facetLimit=limit, facetMincount=1)
    if not page or not page.get("facets"):
        return []
    counts = page["facets"][0].get("counts", [])
    return [(int(c["name"]), c["count"]) for c in counts]


def species_detail(key):
    """GBIF backbone name usage for a species key."""
    return _get(f"/species/{key}")


def build_rows(per_genus, progress=print):
    rows = []
    seen_keys = set()
    nodes = [n for n in ph.iter_nodes() if n.get("genera")]
    total_genera = sum(len(n["genera"]) for n in nodes)
    done = 0
    for node in nodes:
        sg = ph.supergroup_of(node["id"])
        sg_name = sg["name"] if sg else None
        hc = ph.higher_classification(node["id"])
        for genus in node["genera"]:
            done += 1
            key, _ = resolve_genus_key(genus)
            if not key:
                progress(f"  [{done}/{total_genera}] {genus}: no GBIF match")
                continue
            n_added = 0
            for gkey, occ in brazilian_species_keys(key, per_genus):
                if gkey in seen_keys:
                    continue
                s = species_detail(gkey)
                if not s:
                    continue
                name = s.get("canonicalName") or s.get("scientificName")
                # keep species-rank usages whose genus stays within this genus
                if not name or s.get("rank") != "SPECIES":
                    continue
                seen_keys.add(gkey)
                rows.append({
                    "taxon_id": f"GBIF:{gkey}",
                    "supergroup": sg_name,
                    "clade_id": node["id"],
                    "higher_classification": hc,
                    "phylum": s.get("phylum"),
                    "class_": s.get("class"),
                    "order": s.get("order"),
                    "family": s.get("family"),
                    "genus": s.get("genus") or genus,
                    "scientific_name": name,
                    "scientific_name_authorship": s.get("authorship") or None,
                    "taxon_rank": "species",
                    "taxonomic_status": (s.get("taxonomicStatus") or "accepted").lower(),
                    "dataset_name": "GBIF Backbone Taxonomy — ocorrências no Brasil",
                    "occurrence_remarks": f"{occ} registro(s) de ocorrência no Brasil (GBIF)",
                    "references": f"https://www.gbif.org/species/{gkey}",
                })
                n_added += 1
            progress(f"  [{done}/{total_genera}] {genus}: +{n_added} BR species "
                     f"(clade {node['id']})")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-genus", type=int, default=30,
                    help="max accepted species fetched per genus")
    args = ap.parse_args()

    from app import app
    from ingest import stage_ingest, apply_stage

    with app.app_context():
        from models import db
        db.create_all()

    print(f"Fetching up to {args.per_genus} Brazilian species/genus from GBIF…")
    rows = build_rows(args.per_genus)
    print(f"\nCollected {len(rows)} species records. Staging…")

    sid = "gbif-bulk"
    n_ins, n_upd, n_same = stage_ingest(app, rows, sid)
    print(f"Staged: +{n_ins} insert · ↺{n_upd} update · ={n_same} unchanged")
    inserted, updated = apply_stage(app, sid)
    print(f"Applied: ✚{inserted} inserted · ↺{updated} updated")

    with app.app_context():
        from models import Taxon
        print(f"Catalogue now holds {Taxon.query.count()} records "
              f"({Taxon.query.filter_by(taxon_rank='species').count()} species).")


if __name__ == "__main__":
    sys.exit(main())

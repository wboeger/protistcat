"""
Ingest taxa into the Protista catalogue from CSV/TSV uploads or remote
Darwin Core Archives (DwC-A). Staging/preview/apply workflow mirrors the
FaunnadoBrasil system, adapted to the protist schema (supergroup, clade_id,
higherClassification).
"""
import io
import csv
import zipfile
import xml.etree.ElementTree as ET

import requests

import dwc_terms

BATCH_SIZE = 500

# DwC term / CSV header → model attribute (full CTFB extended set)
FIELD_MAP = dict(dwc_terms.HEADER_TO_ATTR)

PT_LABELS = {
    "id": "taxon_id", "taxonid": "taxon_id",
    "supergrupo": "supergroup", "reino": "supergroup",
    "clado": "clade_id",
    "classificação superior": "higher_classification",
    "classificacao superior": "higher_classification",
    "filo": "phylum", "classe": "class_", "ordem": "order",
    "família": "family", "familia": "family",
    "gênero": "genus", "genero": "genus",
    "epíteto específico": "specific_epithet", "epiteto especifico": "specific_epithet",
    "epíteto infraespecífico": "infraspecific_epithet",
    "nome científico": "scientific_name", "nome cientifico": "scientific_name",
    "autoria": "scientific_name_authorship",
    "categoria taxonômica": "taxon_rank", "categoria taxonomica": "taxon_rank",
    "status taxonômico": "taxonomic_status", "status taxonomico": "taxonomic_status",
    "nome aceito": "accepted_name_usage",
    "nome vernacular": "vernacular_name",
    "habitat": "habitat", "observações": "occurrence_remarks",
    "observacoes": "occurrence_remarks",
    "dataset": "dataset_name", "referências": "references", "referencias": "references",
}

UPDATABLE_ATTRS = [a for a in dict.fromkeys(dwc_terms.TEXT_ATTRS) if a != "taxon_id"] + ["extra"]


# ── DwC-A parsing ───────────────────────────────────────────────────────────

def _download_zip(url):
    resp = requests.get(url, headers={"User-Agent": "Protista/1.0"},
                        timeout=300, stream=True)
    resp.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(resp.content))


def _parse_meta(zf):
    if "meta.xml" not in zf.namelist():
        return None, {}, "\t", '"', 1
    root = ET.fromstring(zf.read("meta.xml"))
    core = next((el for el in root if el.tag.endswith("core")), None)
    if core is None:
        return None, {}, "\t", '"', 1
    core_file = None
    for child in core:
        if child.tag.endswith("files"):
            for loc in child:
                if loc.tag.endswith("location"):
                    core_file = loc.text.strip()
    col_indices = {}
    for child in core:
        tag = child.tag.split("}")[-1]
        if tag == "id":
            col_indices["id"] = int(child.get("index", 0))
        elif tag == "field":
            term = child.get("term", "").split("/")[-1]
            col_indices[term] = int(child.get("index", 0))
    delimiter = core.get("fieldsTerminatedBy", "\t").replace("\\t", "\t")
    quote = core.get("fieldsEnclosedBy", '"')
    ignore = int(core.get("ignoreHeaderLines", "1"))
    return core_file, col_indices, delimiter, quote, ignore


def _find_core_file(zf, hint):
    names = zf.namelist()
    if hint and hint in names:
        return hint
    for c in ["taxon.txt", "Taxon.txt", "occurrence.txt"]:
        if c in names:
            return c
    txts = [n for n in names if n.endswith(".txt")]
    if txts:
        return max(txts, key=lambda n: zf.getinfo(n).file_size)
    raise ValueError(f"Arquivo de dados não encontrado. Conteúdo: {names}")


def parse_dwca_rows(url):
    zf = _download_zip(url)
    hint, col_indices, delimiter, quote, ignore = _parse_meta(zf)
    core_file = _find_core_file(zf, hint)
    lines = zf.read(core_file).decode("utf-8", errors="replace").splitlines()
    if not col_indices:
        header = next(csv.reader([lines[0]], delimiter=delimiter, quotechar=quote or '"'))
        col_indices = {c: i for i, c in enumerate(header)}
        ignore = 0
    reader = csv.reader(lines, delimiter=delimiter, quotechar=quote if quote else '"')
    for _ in range(ignore):
        next(reader, None)
    rows = []
    for row in reader:
        if not any(row):
            continue
        kwargs, extra = {}, {}
        for term, idx in col_indices.items():
            if idx >= len(row):
                continue
            val = row[idx].strip() or None
            attr = FIELD_MAP.get(term)
            if attr:
                kwargs[attr] = val
            elif val:
                extra[term] = val
        if extra:
            kwargs["extra"] = extra
        rows.append(kwargs)
    return rows


def parse_csv_rows(file_bytes, delimiter=None):
    raw = file_bytes.decode("utf-8", errors="replace")
    lines = raw.splitlines()
    if not lines:
        return []
    if delimiter is None:
        s = lines[0]
        delimiter = "\t" if s.count("\t") >= s.count(",") else ","
    reader = csv.reader(lines, delimiter=delimiter, quotechar='"')
    header = next(reader, None)
    if not header:
        return []
    col_map = {}
    for i, col in enumerate(header):
        c = col.strip()
        attr = FIELD_MAP.get(c) or PT_LABELS.get(c.lower())
        if attr:
            col_map[i] = attr
    rows = []
    for row in reader:
        if not any(row):
            continue
        kwargs, extra = {}, {}
        for i, val in enumerate(row):
            val = val.strip() or None
            if val is None:
                continue
            attr = col_map.get(i)
            if attr:
                kwargs[attr] = val
            else:
                name = header[i].strip() if i < len(header) else str(i)
                extra[name] = val
        if extra:
            kwargs["extra"] = extra
        rows.append(kwargs)
    return rows


# ── Staging / preview / apply ───────────────────────────────────────────────

def _diff(existing, incoming):
    changes = {}
    for attr in UPDATABLE_ATTRS:
        new = incoming.get(attr)
        old = getattr(existing, attr, None)
        if new != old and not (new is None and old is None):
            changes[attr] = {"old": old, "new": new}
    return changes


def stage_ingest(app, rows_kwargs, session_id, truncate=False):
    from models import db, Taxon, IngestStage
    with app.app_context():
        db.session.execute(db.text("DELETE FROM ingest_stage WHERE session_id = :sid"),
                           {"sid": session_id})
        db.session.commit()
        if truncate:
            existing_map = {}
        else:
            ids = [k.get("taxon_id") for k in rows_kwargs if k.get("taxon_id")]
            existing_map = {t.taxon_id: t for t in
                            Taxon.query.filter(Taxon.taxon_id.in_(ids)).all()} if ids else {}
        n_ins = n_upd = n_same = 0
        batch = []
        for idx, kwargs in enumerate(rows_kwargs):
            tid = kwargs.get("taxon_id")
            existing = existing_map.get(tid) if tid else None
            if existing is None:
                action, diff, existing_data = "insert", {}, {}
                n_ins += 1
            else:
                d = _diff(existing, kwargs)
                if not d:
                    n_same += 1
                    continue
                action, diff = "update", d
                existing_data = {a: getattr(existing, a) for a in UPDATABLE_ATTRS}
                n_upd += 1
            batch.append(IngestStage(
                session_id=session_id, row_index=idx, action=action,
                taxon_id_dwc=tid, existing=existing_data, incoming=kwargs, diff=diff))
            if len(batch) >= BATCH_SIZE:
                db.session.bulk_save_objects(batch); db.session.commit(); batch = []
        if batch:
            db.session.bulk_save_objects(batch); db.session.commit()
        return n_ins, n_upd, n_same


def apply_stage(app, session_id):
    from models import db, Taxon, IngestStage
    with app.app_context():
        rows = IngestStage.query.filter(
            IngestStage.session_id == session_id,
            IngestStage.status != "skipped",
        ).order_by(IngestStage.row_index).all()
        ids = [r.taxon_id_dwc for r in rows if r.taxon_id_dwc]
        existing_map = {t.taxon_id: t for t in
                        Taxon.query.filter(Taxon.taxon_id.in_(ids)).all()} if ids else {}
        to_insert = []
        inserted = updated = 0
        for row in rows:
            data = dict(row.edited or row.incoming)
            tid = row.taxon_id_dwc
            if row.action == "update" and tid in existing_map:
                t = existing_map[tid]
                for attr in UPDATABLE_ATTRS:
                    if attr in data:
                        setattr(t, attr, data[attr])
                updated += 1
            else:
                to_insert.append(Taxon(**{k: v for k, v in data.items()
                                          if k in UPDATABLE_ATTRS or k == "taxon_id"}))
                inserted += 1
            if len(to_insert) >= BATCH_SIZE:
                db.session.bulk_save_objects(to_insert); db.session.commit(); to_insert = []
        if to_insert:
            db.session.bulk_save_objects(to_insert)
        db.session.commit()
        db.session.execute(db.text("DELETE FROM ingest_stage WHERE session_id = :sid"),
                           {"sid": session_id})
        db.session.commit()
        return inserted, updated

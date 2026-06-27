"""
Phylogenetic backbone of the eukaryotes (Protista / basal eukaryotes).

Topology follows Burki, Roger, Brown & Simpson (2020) "The New Tree of
Eukaryotes" (Trends Ecol. Evol. 35:43-55), Figure 1, with subordinate groups
filled from Adl et al. (2019) "Revisions to the Classification, Nomenclature,
and Diversity of Eukaryotes" (J. Eukaryot. Microbiol. 66:4-119).

The tree is a nested structure of clade nodes. Each node:

    id      slug, unique, used in URLs
    name    display name
    rank    informal rank label (supergroup, clade, phylum, ...)
    note    short description shown on the clade page
    fig1    True if the lineage is drawn explicitly in Burki et al. Fig 1
    children   list of subordinate nodes
    genera     representative genera (used to seed the searchable catalogue)

`'Excavates'` is shown in Fig 1 as a dashed, paraphyletic assemblage; here its
former members (Discoba, Metamonada, Malawimonadida, Ancyromonadida) are kept
as independent deep branches, with an `excavate` flag for labelling.
"""

# ──────────────────────────────────────────────────────────────────────────
# The tree
# ──────────────────────────────────────────────────────────────────────────

TREE = {
    "id": "eukaryota",
    "name": "Eukaryota",
    "rank": "domain",
    "note": "All eukaryotes. The vast bulk of eukaryotic diversity is "
            "microbial — the 'protists' (everything that is not an animal, "
            "land plant, or fungus). The deep structure below follows the "
            "phylogenomic consensus of Burki et al. (2020).",
    "fig1": True,
    "children": [

        # ── Amorphea ──────────────────────────────────────────────────────
        {
            "id": "amorphea", "name": "Amorphea", "rank": "supergroup",
            "fig1": True,
            "note": "Amoebozoa + Obazoa (opisthokonts and their protist "
                    "relatives). Robustly supported; ancestrally single "
                    "posterior flagellum.",
            "children": [
                {
                    "id": "amoebozoa", "name": "Amoebozoa", "rank": "clade",
                    "fig1": True,
                    "note": "Lobose amoebae, slime moulds and relatives.",
                    "children": [
                        {"id": "tubulinea", "name": "Tubulinea", "rank": "phylum",
                         "note": "Tubular lobose amoebae and testate amoebae.",
                         "genera": ["Amoeba", "Arcella", "Difflugia", "Chaos"]},
                        {"id": "discosea", "name": "Discosea", "rank": "phylum",
                         "note": "Flattened lobose amoebae, no subpseudopodia.",
                         "genera": ["Acanthamoeba", "Vannella", "Cochliopodium"]},
                        {"id": "evosea", "name": "Evosea", "rank": "phylum",
                         "note": "Includes Eumycetozoa (slime moulds), Variosea "
                                 "and Archamoebae.",
                         "genera": ["Dictyostelium", "Physarum", "Entamoeba",
                                    "Mastigamoeba"]},
                    ],
                },
                {
                    "id": "obazoa", "name": "Obazoa", "rank": "clade",
                    "fig1": True,
                    "note": "Opisthokonta plus the heterotrophic flagellate "
                            "lineages Breviatea and Apusomonadida.",
                    "children": [
                        {"id": "apusomonadida", "name": "Apusomonadida",
                         "rank": "order", "fig1": True,
                         "note": "Gliding biflagellate heterotrophs.",
                         "genera": ["Apusomonas", "Thecamonas"]},
                        {"id": "breviatea", "name": "Breviatea", "rank": "clade",
                         "fig1": True,
                         "note": "Anaerobic/microaerophilic amoeboflagellates.",
                         "genera": ["Breviata", "Pygsuia"]},
                        {
                            "id": "opisthokonta", "name": "Opisthokonta",
                            "rank": "clade", "fig1": True,
                            "note": "Animals, fungi and their unicellular "
                                    "relatives. Only the protist (and fungal) "
                                    "branches are detailed here.",
                            "children": [
                                {"id": "holozoa", "name": "Holozoa", "rank": "clade",
                                 "note": "Metazoa + protistan relatives "
                                         "(choanoflagellates, filastereans, "
                                         "ichthyosporeans, Pluriformea).",
                                 "genera": ["Monosiga", "Salpingoeca",
                                            "Capsaspora", "Sphaeroforma"]},
                                {"id": "holomycota", "name": "Holomycota (Nucletmycea)",
                                 "rank": "clade",
                                 "note": "Fungi + nucleariid amoebae.",
                                 "genera": ["Nuclearia", "Fonticula", "Rozella"]},
                            ],
                        },
                    ],
                },
            ],
        },

        # ── CRuMs ─────────────────────────────────────────────────────────
        {
            "id": "crums", "name": "CRuMs", "rank": "supergroup",
            "fig1": True,
            "note": "Collodictyonids + Rigifilida + Mantamonas. A novel "
                    "supergroup of free-living protists with very different "
                    "morphologies; inferred to branch with Amorphea.",
            "children": [
                {"id": "collodictyonidae", "name": "Collodictyonidae (Diphylleida)",
                 "rank": "family", "fig1": True,
                 "note": "Swimming flagellates with a ventral feeding groove.",
                 "genera": ["Collodictyon", "Diphylleia", "Sulcomonas"]},
                {"id": "rigifilida", "name": "Rigifilida", "rank": "order",
                 "fig1": True,
                 "note": "Filose amoeboid cells with a rigid dorsal pellicle.",
                 "genera": ["Rigifila", "Micronuclearia"]},
                {"id": "mantamonadida", "name": "Mantamonadida", "rank": "order",
                 "fig1": True,
                 "note": "Tiny gliding biflagellate cells.",
                 "genera": ["Mantamonas"]},
            ],
        },

        # ── Archaeplastida ────────────────────────────────────────────────
        {
            "id": "archaeplastida", "name": "Archaeplastida", "rank": "supergroup",
            "fig1": True,
            "note": "Organisms with primary plastids derived directly from "
                    "cyanobacteria: glaucophytes, red algae, and the green "
                    "lineage (green algae + land plants).",
            "children": [
                {"id": "glaucophyta", "name": "Glaucophyta", "rank": "phylum",
                 "fig1": True,
                 "note": "Freshwater algae with cyanelle plastids.",
                 "genera": ["Glaucocystis", "Cyanophora", "Gloeochaete"]},
                {"id": "rhodophyta", "name": "Rhodophyta (+ Rhodelphidia)",
                 "rank": "phylum", "fig1": True,
                 "note": "Red algae; Rhodelphis is a predatory flagellate sister "
                         "to red algae with a non-photosynthetic plastid.",
                 "genera": ["Porphyridium", "Cyanidioschyzon", "Rhodelphis",
                            "Galdieria"]},
                {"id": "chloroplastida", "name": "Chloroplastida (Viridiplantae)",
                 "rank": "clade", "fig1": True,
                 "note": "Green algae and land plants. Only protistan green "
                         "algae are emphasised here.",
                 "children": [
                     {"id": "chlorophyta", "name": "Chlorophyta", "rank": "phylum",
                      "note": "Core green algae.",
                      "genera": ["Chlamydomonas", "Volvox", "Ulva", "Micromonas"]},
                     {"id": "streptophyta", "name": "Streptophyta", "rank": "clade",
                      "note": "Charophyte green algae + land plants.",
                      "genera": ["Spirogyra", "Chara", "Klebsormidium"]},
                 ]},
                {"id": "prasinodermophyta", "name": "Prasinodermophyta",
                 "rank": "phylum",
                 "note": "Early-diverging marine green algae.",
                 "genera": ["Prasinoderma", "Palmophyllum"]},
            ],
        },

        # ── Cryptista ─────────────────────────────────────────────────────
        {
            "id": "cryptista", "name": "Cryptista", "rank": "supergroup",
            "fig1": True,
            "note": "Cryptomonads and relatives. Central to the study of "
                    "secondary plastid origins.",
            "children": [
                {"id": "cryptophyta", "name": "Cryptophyta", "rank": "phylum",
                 "fig1": True,
                 "note": "Cryptomonads; flagellates with red-algal secondary "
                         "plastids retaining a nucleomorph.",
                 "genera": ["Guillardia", "Cryptomonas", "Rhodomonas",
                            "Goniomonas"]},
                {"id": "katablepharidacea", "name": "Katablepharidacea",
                 "rank": "clade", "fig1": True,
                 "note": "Heterotrophic biflagellate predators.",
                 "genera": ["Katablepharis", "Leucocryptos", "Roombia"]},
                {"id": "palpitomonas", "name": "Palpitomonas", "rank": "genus",
                 "fig1": True,
                 "note": "Enigmatic heterotrophic flagellate; deep branch of "
                         "Cryptista.",
                 "genera": ["Palpitomonas"]},
            ],
        },

        # ── Haptista ──────────────────────────────────────────────────────
        {
            "id": "haptista", "name": "Haptista", "rank": "supergroup",
            "fig1": True,
            "note": "Haptophytes + centrohelids. Haptophytes (e.g. "
                    "coccolithophores) are major marine primary producers.",
            "children": [
                {"id": "haptophyta", "name": "Haptophyta (+ Rappemonads)",
                 "rank": "phylum", "fig1": True,
                 "note": "Algae with a haptonema; includes the calcifying "
                         "coccolithophores.",
                 "genera": ["Emiliania", "Phaeocystis", "Prymnesium",
                            "Chrysochromulina"]},
                {"id": "centroplasthelida", "name": "Centroplasthelida (Centrohelida)",
                 "rank": "clade", "fig1": True,
                 "note": "Heliozoa with radiating axopodia from a spherical body.",
                 "genera": ["Raphidiophrys", "Acanthocystis", "Chlamydaster"]},
            ],
        },

        # ── TSAR ──────────────────────────────────────────────────────────
        {
            "id": "tsar", "name": "TSAR", "rank": "supergroup",
            "fig1": True,
            "note": "Telonemia + SAR (Stramenopila, Alveolata, Rhizaria). "
                    "Estimated to hold up to half of all eukaryote species.",
            "children": [
                {"id": "telonemia", "name": "Telonemia", "rank": "phylum",
                 "fig1": True,
                 "note": "Heterotrophic flagellates; sister to SAR.",
                 "genera": ["Telonema"]},
                {
                    "id": "sar", "name": "SAR", "rank": "clade", "fig1": True,
                    "note": "Stramenopila + Alveolata + Rhizaria.",
                    "children": [
                        {
                            "id": "stramenopiles", "name": "Stramenopiles (Heterokonta)",
                            "rank": "clade", "fig1": True,
                            "note": "Cells with tripartite tubular flagellar hairs.",
                            "children": [
                                {"id": "ochrophyta", "name": "Ochrophyta",
                                 "rank": "phylum",
                                 "note": "Photosynthetic stramenopiles: diatoms, "
                                         "brown algae, golden algae.",
                                 "genera": ["Thalassiosira", "Phaeodactylum",
                                            "Ectocarpus", "Ochromonas"]},
                                {"id": "oomycota", "name": "Oomycota",
                                 "rank": "phylum",
                                 "note": "Water moulds and downy mildews.",
                                 "genera": ["Phytophthora", "Saprolegnia",
                                            "Pythium"]},
                                {"id": "bigyra", "name": "Bigyra", "rank": "phylum",
                                 "note": "Heterotrophic stramenopiles "
                                         "(bicosoecids, labyrinthulids, opalines).",
                                 "genera": ["Cafeteria", "Labyrinthula",
                                            "Blastocystis"]},
                            ],
                        },
                        {
                            "id": "alveolata", "name": "Alveolata", "rank": "clade",
                            "fig1": True,
                            "note": "Cells with cortical alveoli.",
                            "children": [
                                {"id": "ciliophora", "name": "Ciliophora",
                                 "rank": "phylum",
                                 "note": "Ciliates; nuclear dualism.",
                                 "genera": ["Paramecium", "Tetrahymena",
                                            "Stentor", "Vorticella"]},
                                {"id": "dinoflagellata", "name": "Dinoflagellata",
                                 "rank": "phylum",
                                 "note": "Dinoflagellates; many photosynthetic, "
                                         "many cause harmful blooms.",
                                 "genera": ["Symbiodinium", "Alexandrium",
                                            "Karenia", "Noctiluca"]},
                                {"id": "apicomplexa", "name": "Apicomplexa",
                                 "rank": "phylum",
                                 "note": "Obligate parasites with an apical complex.",
                                 "genera": ["Plasmodium", "Toxoplasma",
                                            "Cryptosporidium", "Eimeria"]},
                                {"id": "perkinsozoa", "name": "Perkinsozoa",
                                 "rank": "phylum",
                                 "note": "Parasites of molluscs and dinoflagellates.",
                                 "genera": ["Perkinsus"]},
                            ],
                        },
                        {
                            "id": "rhizaria", "name": "Rhizaria", "rank": "clade",
                            "fig1": True,
                            "note": "Mostly amoeboid cells with filose/reticulose "
                                    "pseudopodia.",
                            "children": [
                                {"id": "cercozoa", "name": "Cercozoa",
                                 "rank": "phylum",
                                 "note": "Flagellates and amoebae; includes "
                                         "chlorarachniophyte algae.",
                                 "genera": ["Cercomonas", "Euglypha",
                                            "Bigelowiella", "Paulinella"]},
                                {"id": "retaria", "name": "Retaria", "rank": "clade",
                                 "note": "Foraminifera + Radiolaria.",
                                 "genera": ["Globigerina", "Ammonia",
                                            "Collozoum", "Acantharia"]},
                                {"id": "endomyxa", "name": "Endomyxa",
                                 "rank": "clade",
                                 "note": "Includes plasmodiophorid and "
                                         "ascetosporean parasites.",
                                 "genera": ["Plasmodiophora", "Haplosporidium"]},
                            ],
                        },
                    ],
                },
            ],
        },

        # ── Discoba ───────────────────────────────────────────────────────
        {
            "id": "discoba", "name": "Discoba", "rank": "supergroup",
            "fig1": True, "excavate": True,
            "note": "Euglenozoa + Heterolobosea (= Discicristata) plus Jakobida "
                    "and Tsukubamonas. Part of the dashed, paraphyletic "
                    "'Excavates' of Fig 1.",
            "children": [
                {"id": "euglenozoa", "name": "Euglenozoa", "rank": "phylum",
                 "fig1": True,
                 "note": "Euglenids, kinetoplastids (incl. trypanosomes), "
                         "diplonemids, symbiontids.",
                 "genera": ["Euglena", "Trypanosoma", "Leishmania",
                            "Diplonema", "Bodo"]},
                {"id": "heterolobosea", "name": "Heterolobosea", "rank": "clade",
                 "fig1": True,
                 "note": "Amoeboflagellates that switch between amoeba and "
                         "flagellate forms.",
                 "genera": ["Naegleria", "Acrasis", "Percolomonas"]},
                {"id": "jakobida", "name": "Jakobida", "rank": "order",
                 "fig1": True,
                 "note": "Heterotrophic flagellates with the most bacteria-like "
                         "mitochondrial genomes known.",
                 "genera": ["Jakoba", "Reclinomonas", "Andalucia"]},
                {"id": "tsukubamonas", "name": "Tsukubamonas", "rank": "genus",
                 "fig1": True,
                 "note": "Free-living heterotrophic flagellate; deep branch of "
                         "Discoba.",
                 "genera": ["Tsukubamonas"]},
            ],
        },

        # ── Metamonada ────────────────────────────────────────────────────
        {
            "id": "metamonada", "name": "Metamonada", "rank": "supergroup",
            "fig1": True, "excavate": True,
            "note": "Anaerobic/microaerophilic protists lacking classical "
                    "mitochondria; includes important parasites and gut "
                    "symbionts. Part of the dashed 'Excavates'.",
            "children": [
                {"id": "fornicata", "name": "Fornicata", "rank": "clade",
                 "note": "Diplomonads, retortamonads, Carpediemonas-like taxa.",
                 "genera": ["Giardia", "Spironucleus", "Carpediemonas"]},
                {"id": "parabasalia", "name": "Parabasalia", "rank": "clade",
                 "note": "Parabasalids with a parabasal apparatus; many gut "
                         "symbionts of insects.",
                 "genera": ["Trichomonas", "Trichonympha", "Histomonas"]},
                {"id": "preaxostyla", "name": "Preaxostyla", "rank": "clade",
                 "note": "Oxymonads and Paratrimastix/Trimastix.",
                 "genera": ["Monocercomonoides", "Trimastix", "Paratrimastix"]},
            ],
        },

        # ── Hemimastigophora ──────────────────────────────────────────────
        {
            "id": "hemimastigophora", "name": "Hemimastigophora",
            "rank": "supergroup", "fig1": True,
            "note": "Free-living predatory protists with two rows of flagella. "
                    "Phylogenomics places them as one of the deepest, "
                    "independent eukaryote lineages — proposed as its own "
                    "supergroup.",
            "genera": ["Spironema", "Hemimastix", "Stereonema"],
        },

        # ── Malawimonadida ────────────────────────────────────────────────
        {
            "id": "malawimonadida", "name": "Malawimonadida",
            "rank": "deep lineage", "fig1": True, "excavate": True,
            "note": "Small free-living biflagellate 'excavate' protists of "
                    "uncertain deep placement.",
            "genera": ["Malawimonas", "Gefionella"],
        },

        # ── Ancyromonadida ────────────────────────────────────────────────
        {
            "id": "ancyromonadida", "name": "Ancyromonadida (Planomonadida)",
            "rank": "deep lineage", "fig1": True, "excavate": True,
            "note": "Tiny gliding biflagellates; an isolated deep branch shown "
                    "with the 'excavates' in Fig 1.",
            "genera": ["Ancyromonas", "Fabomonas", "Planomonas"],
        },

        # ── Orphan / incertae sedis lineages near the root ────────────────
        {
            "id": "picozoa", "name": "Picozoa", "rank": "orphan lineage",
            "fig1": True,
            "note": "Tiny marine heterotrophic flagellates ('picobiliphytes' "
                    "as first described); position near the root unresolved.",
            "genera": ["Picomonas"],
        },
        {
            "id": "ancoracysta", "name": "Ancoracysta", "rank": "orphan lineage",
            "fig1": True,
            "note": "Predatory flagellate with extrusive ancoracysts; an "
                    "'orphan' lineage of uncertain position, possibly sister "
                    "to Haptista.",
            "genera": ["Ancoracysta"],
        },
    ],
}


# ──────────────────────────────────────────────────────────────────────────
# Navigation helpers
# ──────────────────────────────────────────────────────────────────────────

def _index(node, parent, idx, by_id, parent_of):
    by_id[node["id"]] = node
    parent_of[node["id"]] = parent
    for child in node.get("children", []):
        _index(child, node, idx, by_id, parent_of)


_BY_ID = {}
_PARENT_OF = {}
_index(TREE, None, 0, _BY_ID, _PARENT_OF)


def get_node(node_id):
    return _BY_ID.get(node_id)


def get_parent(node_id):
    return _PARENT_OF.get(node_id)


def get_path(node_id):
    """Root-to-node list of nodes (breadcrumb)."""
    path = []
    cur = _BY_ID.get(node_id)
    while cur is not None:
        path.append(cur)
        cur = _PARENT_OF.get(cur["id"])
    return list(reversed(path))


def iter_nodes(node=None):
    node = node or TREE
    yield node
    for child in node.get("children", []):
        yield from iter_nodes(child)


def leaf_genera(node):
    """All representative genera at or below a node."""
    out = []
    for n in iter_nodes(node):
        out.extend(n.get("genera", []) or [])
    return out


def higher_classification(node_id):
    """Pipe-delimited DwC higherClassification string (excludes the domain)."""
    path = get_path(node_id)
    return " | ".join(n["name"] for n in path[1:])


def supergroup_of(node_id):
    """The supergroup ancestor (rank == 'supergroup'), or the node itself."""
    for n in get_path(node_id):
        if n.get("rank") in ("supergroup",):
            return n
    # orphan / deep lineages: return the node itself
    return _BY_ID.get(node_id)


# ──────────────────────────────────────────────────────────────────────────
# SVG cladogram renderer (rectangular, clickable)
# ──────────────────────────────────────────────────────────────────────────

def render_cladogram(root, max_depth, link_fn, row_h=30, col_w=210,
                     pad_x=14, pad_y=20):
    """
    Render a rectangular cladogram as inline SVG.

    root      starting node
    max_depth how many levels below `root` to draw (root = level 0)
    link_fn   callable(node) -> url or None; nodes with a url become <a> links
    """
    # collect visible nodes with depth, truncating children beyond max_depth
    rows = []           # leaf order

    def walk(node, depth):
        kids = node.get("children", []) if depth < max_depth else []
        if not kids:
            node["_y"] = len(rows) * row_h + pad_y
            rows.append(node)
        else:
            ys = [walk(k, depth + 1) for k in kids]
            node["_y"] = (min(ys) + max(ys)) / 2
        node["_x"] = depth * col_w + pad_x
        node["_kids"] = kids
        return node["_y"]

    walk(root, 0)

    nodes = list(_visible(root, 0, max_depth))
    height = len(rows) * row_h + pad_y * 2
    max_depth_seen = max(n["_depth"] for n in nodes)
    width = (max_depth_seen + 1) * col_w + 80

    parts = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
             f'class="cladogram" role="img" '
             f'xmlns="http://www.w3.org/2000/svg" '
             f'xmlns:xlink="http://www.w3.org/1999/xlink">']

    # connectors
    for n in nodes:
        kids = n.get("_kids", [])
        if not kids:
            continue
        px = n["_x"]
        # elbow: vertical bar spanning children, horizontal stubs
        ys = [k["_y"] for k in kids]
        parts.append(f'<path class="branch" d="M{px+ _LABEL_W} {min(ys):.1f} '
                     f'L{px+_LABEL_W} {max(ys):.1f}"/>')
        for k in kids:
            parts.append(
                f'<path class="branch" d="M{px+_LABEL_W} {k["_y"]:.1f} '
                f'L{k["_x"]:.1f} {k["_y"]:.1f}"/>')

    # nodes
    for n in nodes:
        x, y = n["_x"], n["_y"]
        url = link_fn(n)
        cls = "node"
        if n.get("rank") == "supergroup":
            cls += " node-super"
        if n.get("excavate"):
            cls += " node-excavate"
        label = _esc(n["name"])
        rank = _esc(n.get("rank", ""))
        tip = url is not None
        g_open = (f'<a xlink:href="{url}" class="{cls}{" node-link" if tip else ""}">'
                  if url else f'<g class="{cls}">')
        g_close = '</a>' if url else '</g>'
        parts.append(g_open)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="node-dot"/>')
        parts.append(f'<text x="{x+9:.1f}" y="{y-2:.1f}" class="node-name">{label}</text>')
        if rank:
            parts.append(f'<text x="{x+9:.1f}" y="{y+10:.1f}" class="node-rank">{rank}</text>')
        parts.append(g_close)

    parts.append('</svg>')
    return "".join(parts)


_LABEL_W = 0   # connectors start at node x (labels extend to the right)


def _visible(node, depth, max_depth):
    node["_depth"] = depth
    yield node
    if depth < max_depth:
        for k in node.get("children", []):
            yield from _visible(k, depth + 1, max_depth)


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))

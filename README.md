# Catálogo dos Protistas (eucariontes basais)

Sistema online inspirado no **FaunnadoBrasil** (Catálogo Taxonômico da Fauna do
Brasil), recriado para os **protistas / eucariontes basais**.

A primeira página da busca pública é a **Nova Árvore dos Eucariontes** de
Burki, Roger, Brown & Simpson (2020, *Trends Ecol. Evol.* 35:43–55), **Figura 1**,
renderizada como cladograma clicável. Cada supergrupo / linhagem profunda abre
uma subpágina com o **esquema de relações internas**, igualmente clicável, que
desce pela hierarquia até os grupos terminais e, daí, para a busca de táxons.

A classificação dos grupos subordinados segue **Adl et al. (2019)**, garantindo
que os principais grupos de protistas estejam representados.

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `phylogeny.py` | Backbone filogenético (Fig 1 + Adl 2019) + renderizador SVG do cladograma clicável |
| `models.py`    | Modelo `Taxon` (Darwin Core + campos `supergroup`, `clade_id`, `higher_classification`) |
| `app.py`       | App Flask: filogenia, subpáginas de clados, busca, detalhe de táxon, export DwC-A/CSV, *seed* |
| `templates/`   | `base`, `index` (Fig 1), `clade`, `search`, `taxon` |

## Campos / Darwin Core

Mantém os campos DwC do FaunnadoBrasil e acrescenta o rank **supergrupo**
(protistas não cabem em "kingdom") e `higherClassification` (caminho completo na
árvore). No export DwC-A o supergrupo é mapeado para o termo `dwc:kingdom` por
compatibilidade.

## Rodar

```bash
pip install -r requirements.txt
python app.py          # cria o SQLite, faz o seed dos gêneros representativos, sobe em :8080
```

Usuário admin padrão: **admin / admin** (mude via env `ADMIN_USER`,
`ADMIN_PASSWORD`, `ADMIN_EMAIL`).

### Rotas

**Público:** `/` (filogenia) · `/clade/<id>` · `/busca` · `/taxon/<id>` ·
`/download` (CSV) · `/api`, `/api/taxa`, `/api/taxa/<id>`, `/api/dwca`,
`/api/phylogeny` · `/health`.

**Workspace (login):** `/workspace/login`, `/workspace/` (painel + auditoria),
`/workspace/taxon/<id>/edit` (edição com histórico).

**Admin:** `/admin/ingest` (upload CSV/TSV + URLs DwC-A → pré-visualização →
confirmar/cancelar, com pular linhas) · `/admin/users` (criar/ativar).

## Fontes

- Burki F., Roger A.J., Brown M.W., Simpson A.G.B. (2020) The New Tree of
  Eukaryotes. *Trends Ecol. Evol.* 35:43–55. https://doi.org/10.1016/j.tree.2019.08.008
- Adl S.M. et al. (2019) Revisions to the Classification, Nomenclature, and
  Diversity of Eukaryotes. *J. Eukaryot. Microbiol.* 66:4–119.

## Deploy (Railway)

Persistência via **volume** montado (SQLite no volume). No primeiro boot,
`startup.py` copia o banco semente `protista_seed.db` (já com as 324 espécies
brasileiras) para o volume; depois é idempotente. O usuário admin é criado a
partir de `ADMIN_PASSWORD` (o semente não contém usuários).

Variáveis de ambiente:

| Var | Uso |
|---|---|
| `RAILWAY_VOLUME_MOUNT_PATH` | definido pela Railway ao anexar o volume; caminho do SQLite |
| `SECRET_KEY` | chave de sessão Flask |
| `ADMIN_USER` / `ADMIN_PASSWORD` / `ADMIN_EMAIL` | admin criado no 1º boot |
| `DATABASE_URL` | opcional — usar Postgres em vez de SQLite |

Start: `python startup.py && gunicorn app:app --bind 0.0.0.0:$PORT` (em `Procfile` e `railway.json`).

Para reingerir/atualizar dados do GBIF no volume: `railway run python gbif_ingest.py --per-genus 40`.

## Status

Fase 1 (site público: filogenia clicável + busca + DwC-A) e Fase 2 (workspace de
edição com auditoria, ingestão administrativa com pré-visualização, gestão de
usuários e API JSON) — concluídas, espelhando o FaunnadoBrasil.

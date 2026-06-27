"""
Gera o Manual do Catálogo dos Protistas em PDF.
Uso: python3 generate_manual.py   ->  static/Manual_Protistas.pdf
"""
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)

OUTPUT = os.path.join("static", "Manual_Protistas.pdf")

PRIMARY      = colors.HexColor("#185a6d")
PRIMARY_LITE = colors.HexColor("#2f93a8")
SECONDARY    = colors.HexColor("#6b4f9e")
ACCENT       = colors.HexColor("#d98c3f")
LIGHT_BG     = colors.HexColor("#e6f1f3")
BORDER       = colors.HexColor("#cddde0")
MUTED        = colors.HexColor("#5d7176")


def styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("TitleBig", parent=s["Title"], fontSize=26,
                         textColor=PRIMARY, spaceAfter=6, leading=30))
    s.add(ParagraphStyle("Sub", parent=s["Normal"], fontSize=12,
                         textColor=MUTED, alignment=TA_CENTER, spaceAfter=18))
    s.add(ParagraphStyle("H1", parent=s["Heading1"], fontSize=16,
                         textColor=PRIMARY, spaceBefore=16, spaceAfter=8))
    s.add(ParagraphStyle("H2", parent=s["Heading2"], fontSize=12.5,
                         textColor=SECONDARY, spaceBefore=10, spaceAfter=5))
    s.add(ParagraphStyle("Body", parent=s["Normal"], fontSize=10.2,
                         leading=15, alignment=TA_JUSTIFY, spaceAfter=6))
    s.add(ParagraphStyle("Bul", parent=s["Normal"], fontSize=10.2,
                         leading=15, leftIndent=14, bulletIndent=4, spaceAfter=3))
    s.add(ParagraphStyle("Note", parent=s["Normal"], fontSize=9.5,
                         leading=13, textColor=MUTED, spaceAfter=6))
    s.add(ParagraphStyle("Cell", parent=s["Normal"], fontSize=9, leading=12))
    s.add(ParagraphStyle("CellB", parent=s["Normal"], fontSize=9, leading=12,
                         textColor=PRIMARY, fontName="Helvetica-Bold"))
    return s


def hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER,
                      spaceBefore=6, spaceAfter=10)


def info_table(rows, S, col_widths):
    data = [[Paragraph(c, S["CellB"] if j == 0 else S["Cell"]) for j, c in enumerate(r)]
            for r in rows]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build():
    os.makedirs("static", exist_ok=True)
    S = styles()
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=1.8*cm, bottomMargin=1.8*cm,
                            title="Manual do Catálogo dos Protistas")
    E = []
    P = lambda t, st="Body": E.append(Paragraph(t, S[st]))
    def B(t): E.append(Paragraph(f"• {t}", S["Bul"]))

    # ── Cover ──
    E.append(Spacer(1, 3*cm))
    P("🦠 Catálogo dos Protistas", "TitleBig")
    P("Eucariontes basais — Manual do Sistema", "Sub")
    E.append(hr())
    P("Sistema online de organização taxonômica e busca da diversidade de "
      "protistas (eucariontes basais), com a filogenia navegável da "
      "<i>Nova Árvore dos Eucariontes</i> e dados de espécies brasileiras "
      "obtidos do GBIF.", "Body")
    P(f"Versão do documento: {datetime.now().strftime('%d/%m/%Y')}", "Note")
    E.append(PageBreak())

    # ── 1. Visão geral ──
    P("1. Visão geral", "H1"); E.append(hr())
    P("O catálogo organiza a diversidade dos protistas seguindo o consenso "
      "filogenômico de Burki, Roger, Brown &amp; Simpson (2020), <i>The New "
      "Tree of Eukaryotes</i> (Figura 1), com os grupos subordinados "
      "detalhados a partir de Adl et al. (2019). Diferente dos catálogos de "
      "animais, plantas ou fungos, os protistas não cabem em um único reino: "
      "o nível superior aqui é o <b>supergrupo</b> (p.ex. TSAR, Amorphea, "
      "Archaeplastida).", "Body")
    P("O sistema tem duas faces:", "Body")
    B("<b>Público</b> — qualquer pessoa navega na filogenia clicável, busca "
      "táxons e baixa dados (CSV / Darwin Core Archive / API JSON).")
    B("<b>Acesso de especialistas (Workspace)</b> — pesquisadores autenticados "
      "editam registros com histórico de auditoria; administradores ingerem "
      "novos dados e gerenciam usuários.")

    # ── 2. A filogenia navegável ──
    P("2. A filogenia navegável", "H1"); E.append(hr())
    P("A página inicial apresenta a <i>Nova Árvore dos Eucariontes</i> como um "
      "cladograma clicável. Cada <b>supergrupo</b> ou linhagem profunda abre "
      "uma subpágina com o esquema de relações internas, também clicável, que "
      "desce na hierarquia até os grupos terminais e, daí, para a busca de "
      "táxons.", "Body")
    P("Como navegar:", "H2")
    B("Clique em um supergrupo na árvore (ou nos cartões abaixo dela).")
    B("Na subpágina, clique em um grupo subordinado para descer um nível.")
    B("Nos grupos terminais, o botão leva à busca já filtrada por aquele clado.")
    B("As migalhas de pão (topo da página) permitem voltar a qualquer nível.")
    P("Os supergrupos e linhagens profundas incluídos: TSAR, Haptista, "
      "Cryptista, Archaeplastida, Amorphea, CRuMs, Discoba, Metamonada, "
      "Hemimastigophora, Malawimonadida, Ancyromonadida, além de linhagens "
      "órfãs (Picozoa, Ancoracysta). As linhagens 'Excavates' aparecem "
      "marcadas como agrupamento parafilético.", "Note")

    # ── 3. Busca e download ──
    P("3. Busca e download de dados", "H1"); E.append(hr())
    P("A página <b>Busca</b> filtra por texto livre (nome científico, gênero, "
      "família), supergrupo, gênero e clado. Cada resultado abre a ficha do "
      "táxon, com a classificação completa e o caminho na filogenia.", "Body")
    P("Formatos de exportação:", "H2")
    B("<b>CSV</b> — planilha com todos os campos, respeitando os filtros ativos.")
    B("<b>Darwin Core Archive (DwC-A)</b> — pacote .zip (meta.xml + taxon.txt) "
      "no padrão TDWG, pronto para o GBIF/IPT.")
    B("<b>API JSON</b> — <font face='Courier'>/api/taxa</font>, "
      "<font face='Courier'>/api/taxa/&lt;id&gt;</font>, "
      "<font face='Courier'>/api/phylogeny</font> e "
      "<font face='Courier'>/api/dwca</font>.")

    # ── 4. Campos (Darwin Core) ──
    P("4. Campos e padrão Darwin Core", "H1"); E.append(hr())
    P("Os campos seguem o Darwin Core, com duas adições para acomodar a "
      "filogenia dos protistas:", "Body")
    info_rows = [
        ["Campo", "Descrição"],
        ["supergroup", "Supergrupo eucarionte (nível superior; exportado como dwc:kingdom)."],
        ["higherClassification", "Caminho completo na árvore (separado por |)."],
        ["clade (id)", "Nó da filogenia ao qual o registro está vinculado."],
        ["phylum / class / order / family / genus", "Hierarquia linneana clássica."],
        ["scientificName / scientificNameAuthorship", "Nome científico e autoria."],
        ["taxonRank / taxonomicStatus", "Categoria e status taxonômico."],
        ["habitat / occurrenceRemarks", "Habitat e observações (p.ex. ocorrências no Brasil)."],
        ["datasetName / references", "Fonte do dado e referência."],
    ]
    E.append(info_table(info_rows, S, [5.2*cm, 10.6*cm]))
    E.append(Spacer(1, 6))

    # ── 5. Acesso de especialistas ──
    P("5. Acesso de especialistas (Workspace)", "H1"); E.append(hr())
    P("O <b>Acesso de especialistas</b> fica no canto superior direito de "
      "qualquer página (<i>Acesso de especialistas ›</i>) e também na página "
      "inicial. Requer usuário e senha fornecidos pelo administrador.", "Body")
    P("Funções do editor:", "H2")
    B("Localizar um táxon na busca e abrir <i>✎ Editar</i>.")
    B("Alterar qualquer campo; cada alteração registra autor, data e nota.")
    B("Consultar o histórico de edições do registro e do sistema.")
    P("Funções do administrador:", "H2")
    B("<b>Ingestão</b> — enviar CSV/TSV e/ou URLs de DwC-A; o sistema mostra "
      "uma pré-visualização (inserções, atualizações com diferenças campo a "
      "campo, e linhas inalteradas) antes de gravar. É possível pular linhas e "
      "confirmar ou cancelar.")
    B("<b>Usuários</b> — criar editores/administradores e ativar/desativar contas.")
    P("Nada é gravado no catálogo até a confirmação na pré-visualização.", "Note")

    # ── 6. Dados de espécies brasileiras ──
    P("6. Dados de espécies brasileiras (GBIF)", "H1"); E.append(hr())
    P("Além dos gêneros de referência do backbone, o catálogo é populado com "
      "espécies de protistas com registros de ocorrência no <b>Brasil</b>, "
      "obtidas da Taxonomia Backbone do GBIF (facetamento de ocorrências por "
      "espécie, país = BR). Cada registro guarda a autoria, a classificação do "
      "GBIF e o número de ocorrências no Brasil.", "Body")
    P("Para reingerir ou atualizar: <font face='Courier'>python gbif_ingest.py "
      "--per-genus 40</font>.", "Note")

    # ── 7. Fontes ──
    P("7. Fontes e licença", "H1"); E.append(hr())
    B("Burki F., Roger A.J., Brown M.W., Simpson A.G.B. (2020) The New Tree of "
      "Eukaryotes. <i>Trends Ecol. Evol.</i> 35:43–55.")
    B("Adl S.M. et al. (2019) Revisions to the Classification, Nomenclature, "
      "and Diversity of Eukaryotes. <i>J. Eukaryot. Microbiol.</i> 66:4–119.")
    B("GBIF.org — Global Biodiversity Information Facility (Backbone Taxonomy).")
    P("Dados sob licença CC BY 4.0.", "Note")

    doc.build(E)
    print(f"Manual gerado: {OUTPUT}")


if __name__ == "__main__":
    build()

import os
import io
import csv
import uuid
import zipfile
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    abort, jsonify, Response, stream_with_context,
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user,
)

from models import db, Taxon, User, AuditLog, IngestStage
import phylogeny as ph
import dwc_terms


def data_dir():
    """Directory for the SQLite file. Prefers the Railway volume mount, then an
    explicit DATA_DIR, then a fixed /data folder; if /data is not writable
    (e.g. local dev without root), falls back to ./instance."""
    for d in (os.environ.get("RAILWAY_VOLUME_MOUNT_PATH"),
              os.environ.get("DATA_DIR"),
              "/data"):
        if not d:
            continue
        try:
            os.makedirs(d, exist_ok=True)
            if os.access(d, os.W_OK):
                return d
        except OSError:
            continue
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance")
    os.makedirs(d, exist_ok=True)
    return d


def db_path():
    return os.path.join(data_dir(), "protista.db")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")

    database_url = os.environ.get("DATABASE_URL", "")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{db_path()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.jinja_env.globals["getattr"] = getattr

    login_manager = LoginManager(app)
    login_manager.login_view = "workspace_login"
    login_manager.login_message = "Faça login para acessar o Workspace."

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    _register_routes(app)
    return app


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# Darwin Core export fields — single source of truth in dwc_terms.py
DWC_FIELDS = dwc_terms.EXPORT_FIELDS
CSV_COLUMNS = [(attr, csv) for csv, attr, _ in dwc_terms.TERMS]


def _csv_response(taxa, filename):
    def generate():
        buf = io.StringIO(); w = csv.writer(buf)
        w.writerow([c for _, c in CSV_COLUMNS]); yield buf.getvalue()
        for t in taxa:
            buf = io.StringIO(); w = csv.writer(buf)
            w.writerow([getattr(t, a) or "" for a, _ in CSV_COLUMNS])
            yield buf.getvalue()
    return Response(stream_with_context(generate()),
                    mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def _filtered(query):
    q          = request.args.get("q", "").strip()
    supergroup = request.args.get("supergroup", "").strip()
    clade      = request.args.get("clade", "").strip()
    phylum     = request.args.get("phylum", "").strip()
    genus      = request.args.get("genus", "").strip()
    rank       = request.args.get("taxon_rank", "").strip()
    status     = request.args.get("status", "").strip()
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(
            Taxon.scientific_name.ilike(like),
            Taxon.vernacular_name.ilike(like),
            Taxon.genus.ilike(like),
            Taxon.family.ilike(like),
        ))
    if supergroup: query = query.filter(Taxon.supergroup.ilike(f"%{supergroup}%"))
    if clade:      query = query.filter(Taxon.clade_id == clade)
    if phylum:     query = query.filter(Taxon.phylum.ilike(f"%{phylum}%"))
    if genus:      query = query.filter(Taxon.genus.ilike(f"%{genus}%"))
    if rank:       query = query.filter(Taxon.taxon_rank == rank)
    if status:     query = query.filter(Taxon.taxonomic_status == status)
    return query


def _register_routes(app):

    # ── Public phylogeny ──────────────────────────────────────────────────

    @app.route("/")
    def index():
        """First page: the New Tree of Eukaryotes (Burki et al. 2020, Fig 1),
        clickable to each supergroup / deep lineage."""
        svg = ph.render_cladogram(
            ph.TREE, max_depth=2,
            link_fn=lambda n: (url_for("clade", clade_id=n["id"])
                               if n["id"] != "eukaryota" else None),
        )
        return render_template("index.html", svg=svg, tree=ph.TREE)

    @app.route("/clade/<clade_id>")
    def clade(clade_id):
        node = ph.get_node(clade_id)
        if not node:
            abort(404)
        # scheme of relationships within this clade, clickable to subordinates
        svg = ph.render_cladogram(
            node, max_depth=2,
            link_fn=lambda n: (url_for("clade", clade_id=n["id"])
                               if n["id"] != clade_id and n.get("children")
                               else (url_for("search", clade=n["id"])
                                     if n["id"] != clade_id else None)),
        )
        children = node.get("children", [])
        n_taxa = Taxon.query.filter_by(clade_id=clade_id).count() if not children else None
        return render_template(
            "clade.html", node=node, svg=svg,
            path=ph.get_path(clade_id), children=children,
            parent=ph.get_parent(clade_id), n_taxa=n_taxa,
        )

    # ── Catalogue search ──────────────────────────────────────────────────

    @app.route("/busca")
    def search():
        page = request.args.get("page", 1, type=int)
        clade = request.args.get("clade", "").strip()
        query = _filtered(Taxon.query).order_by(Taxon.scientific_name)
        pagination = query.paginate(page=page, per_page=50, error_out=False)
        supergroups = [r[0] for r in db.session.query(Taxon.supergroup)
                       .distinct().order_by(Taxon.supergroup) if r[0]]
        clade_node = ph.get_node(clade) if clade else None
        args = {k: v for k, v in request.args.items() if k != "page" and v}
        return render_template(
            "search.html", pagination=pagination, taxa=pagination.items,
            supergroups=supergroups, clade_node=clade_node, args=args,
        )

    @app.route("/taxon/<int:taxon_id>")
    def taxon(taxon_id):
        t = db.get_or_404(Taxon, taxon_id)
        node = ph.get_node(t.clade_id) if t.clade_id else None
        path = ph.get_path(t.clade_id) if node else []
        return render_template("taxon.html", t=t, node=node, path=path,
                               terms=dwc_terms.TERMS)

    @app.route("/download")
    def download():
        query = _filtered(Taxon.query).order_by(Taxon.scientific_name)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        return _csv_response(query.yield_per(500), f"protista_{ts}.csv")

    @app.route("/api/dwca")
    def api_dwca():
        query = _filtered(Taxon.query).order_by(Taxon.scientific_name)
        field_xml = "\n".join(
            f'    <field index="{i+1}" term="{uri}"/>'
            for i, (_, uri) in enumerate(DWC_FIELDS))
        meta_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<archive xmlns="http://rs.tdwg.org/dwc/text/">
  <core encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\n"
        fieldsEnclosedBy="" ignoreHeaderLines="1"
        rowType="http://rs.tdwg.org/dwc/terms/Taxon">
    <files><location>taxon.txt</location></files>
    <id index="0"/>
{field_xml}
  </core>
</archive>"""
        buf = io.StringIO()
        w = csv.writer(buf, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow(["id"] + [a for a, _ in DWC_FIELDS])
        for t in query.yield_per(500):
            w.writerow([t.id] + [getattr(t, a) or "" for a, _ in DWC_FIELDS])
        zbuf = io.BytesIO()
        with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("meta.xml", meta_xml)
            zf.writestr("taxon.txt", buf.getvalue())
        zbuf.seek(0)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        return Response(zbuf.read(), mimetype="application/zip",
                        headers={"Content-Disposition":
                                 f'attachment; filename="protista_dwca_{ts}.zip"'})

    # ── Workspace (login + edit + audit) ──────────────────────────────────

    @app.route("/workspace/login", methods=["GET", "POST"])
    def workspace_login():
        if current_user.is_authenticated:
            return redirect(url_for("workspace_dashboard"))
        if request.method == "POST":
            u = User.query.filter_by(username=request.form.get("username", "").strip()).first()
            if u and u.check_password(request.form.get("password", "")) and u.is_active:
                login_user(u, remember=True)
                return redirect(request.args.get("next") or url_for("workspace_dashboard"))
            flash("Usuário ou senha inválidos.", "error")
        return render_template("workspace/login.html")

    @app.route("/workspace/logout")
    @login_required
    def workspace_logout():
        logout_user()
        return redirect(url_for("workspace_login"))

    @app.route("/workspace/")
    @login_required
    def workspace_dashboard():
        recent = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(30).all()
        total = Taxon.query.count()
        return render_template("workspace/dashboard.html", recent_logs=recent, total_taxa=total)

    EDITABLE = [a for a in dict.fromkeys(dwc_terms.TEXT_ATTRS) if a != "taxon_id"]

    @app.route("/workspace/taxon/<int:taxon_id>/edit", methods=["GET", "POST"])
    @login_required
    def workspace_edit(taxon_id):
        t = db.get_or_404(Taxon, taxon_id)
        if request.method == "POST":
            changes = {}
            for field in EDITABLE:
                new = request.form.get(field, "").strip() or None
                old = getattr(t, field)
                if new != old:
                    changes[field] = {"old": old, "new": new}
                    setattr(t, field, new)
            if changes:
                t.modified_at = datetime.now(timezone.utc)
                t.modified_by_id = current_user.id
                db.session.add(AuditLog(taxon_id=t.id, user_id=current_user.id,
                                        changes=changes,
                                        note=request.form.get("note", "").strip() or None))
                db.session.commit()
                flash(f"{len(changes)} campo(s) atualizado(s).", "success")
            else:
                flash("Nenhuma alteração detectada.", "info")
            return redirect(url_for("workspace_edit", taxon_id=t.id))
        logs = t.audit_logs.order_by(AuditLog.timestamp.desc()).limit(10).all()
        return render_template("workspace/edit.html", t=t, logs=logs, fields=EDITABLE)

    # ── Admin: ingest ─────────────────────────────────────────────────────

    @app.route("/admin/ingest", methods=["GET", "POST"])
    @admin_required
    def admin_ingest():
        if request.method == "POST":
            from ingest import parse_dwca_rows, parse_csv_rows, stage_ingest
            truncate = request.form.get("truncate") == "1"
            sid = str(uuid.uuid4())
            rows = []
            for f in request.files.getlist("csv_file"):
                if not f or not f.filename:
                    continue
                try:
                    rows.extend(parse_csv_rows(f.read()))
                except Exception as e:
                    flash(f"Erro no arquivo '{f.filename}': {e}", "error")
                    return redirect(url_for("admin_ingest"))
            urls = []
            for chunk in request.form.getlist("url"):
                urls.extend(u.strip() for u in chunk.splitlines() if u.strip())
            for url in urls:
                try:
                    rows.extend(parse_dwca_rows(url))
                except Exception as e:
                    flash(f"Erro na URL '{url}': {e}", "error")
                    return redirect(url_for("admin_ingest"))
            if not rows:
                flash("Nenhuma fonte fornecida ou arquivo vazio.", "error")
                return redirect(url_for("admin_ingest"))
            n_ins, n_upd, n_same = stage_ingest(app, rows, sid, truncate=truncate)
            return redirect(url_for("admin_ingest_preview", sid=sid,
                                    n_ins=n_ins, n_upd=n_upd, n_same=n_same))
        return render_template("workspace/admin_ingest.html")

    @app.route("/admin/ingest/preview")
    @admin_required
    def admin_ingest_preview():
        sid = request.args.get("sid", "")
        page = request.args.get("page", 1, type=int)
        filt = request.args.get("filter", "")
        q = IngestStage.query.filter_by(session_id=sid)
        if filt:
            q = q.filter_by(action=filt)
        pag = q.order_by(IngestStage.row_index).paginate(page=page, per_page=50, error_out=False)
        return render_template("workspace/ingest_preview.html", sid=sid,
                               pagination=pag, rows=pag.items, filter_action=filt,
                               n_ins=request.args.get("n_ins", 0, type=int),
                               n_upd=request.args.get("n_upd", 0, type=int),
                               n_same=request.args.get("n_same", 0, type=int))

    @app.route("/admin/ingest/row/<int:row_id>/skip", methods=["POST"])
    @admin_required
    def admin_ingest_skip(row_id):
        row = db.get_or_404(IngestStage, row_id)
        row.status = "skipped" if row.status != "skipped" else "pending"
        db.session.commit()
        return redirect(request.referrer or url_for("admin_ingest_preview", sid=row.session_id))

    @app.route("/admin/ingest/confirm", methods=["POST"])
    @admin_required
    def admin_ingest_confirm():
        from ingest import apply_stage
        sid = request.form.get("sid", "")
        if not sid:
            flash("Sessão inválida.", "error")
            return redirect(url_for("admin_ingest"))
        try:
            ins, upd = apply_stage(app, sid)
            flash(f"Ingestão concluída: ✚ {ins:,} inseridos · ↺ {upd:,} atualizados.", "success")
        except Exception as e:
            flash(f"Erro ao aplicar: {e}", "error")
        return redirect(url_for("workspace_dashboard"))

    @app.route("/admin/ingest/cancel", methods=["POST"])
    @admin_required
    def admin_ingest_cancel():
        sid = request.form.get("sid", "")
        if sid:
            db.session.execute(db.text("DELETE FROM ingest_stage WHERE session_id = :sid"),
                               {"sid": sid})
            db.session.commit()
        flash("Ingestão cancelada.", "info")
        return redirect(url_for("admin_ingest"))

    # ── Admin: users ──────────────────────────────────────────────────────

    @app.route("/admin/users", methods=["GET", "POST"])
    @admin_required
    def admin_users():
        if request.method == "POST":
            action = request.form.get("action")
            if action == "create":
                username = request.form.get("username", "").strip()
                email = request.form.get("email", "").strip()
                password = request.form.get("password", "")
                role = request.form.get("role", "editor")
                if not username or not email or not password:
                    flash("Preencha todos os campos.", "error")
                elif User.query.filter_by(username=username).first():
                    flash("Usuário já existe.", "error")
                else:
                    u = User(username=username, email=email, role=role)
                    u.set_password(password)
                    db.session.add(u); db.session.commit()
                    flash(f"Usuário '{username}' criado.", "success")
            elif action == "toggle":
                u = db.session.get(User, request.form.get("user_id", type=int))
                if u and u.id != current_user.id:
                    u.active = not u.active; db.session.commit()
                    flash(f"Usuário '{u.username}' {'ativado' if u.active else 'desativado'}.", "success")
        users = User.query.order_by(User.username).all()
        return render_template("workspace/admin_users.html", users=users)

    # ── JSON API ──────────────────────────────────────────────────────────

    def _taxon_to_dict(t, full=False):
        d = {
            "id": t.id, "taxonID": t.taxon_id,
            "scientificName": t.scientific_name,
            "scientificNameAuthorship": t.scientific_name_authorship,
            "vernacularName": t.vernacular_name,
            "taxonRank": t.taxon_rank, "taxonomicStatus": t.taxonomic_status,
            "supergroup": t.supergroup, "cladeID": t.clade_id,
            "higherClassification": t.higher_classification,
            "phylum": t.phylum, "class": t.class_, "order": t.order,
            "family": t.family, "genus": t.genus,
        }
        if full:
            for csv, attr, _ in dwc_terms.TERMS:
                d.setdefault(csv, getattr(t, attr))
            d["extra"] = t.extra
        return {k: v for k, v in d.items() if v is not None}

    @app.route("/api")
    def api_index():
        base = request.host_url.rstrip("/")
        return jsonify({
            "version": "1.0",
            "description": "Catálogo dos Protistas — API pública",
            "endpoints": {
                "taxa_search": f"{base}/api/taxa",
                "params": ["q", "supergroup", "clade", "phylum", "genus",
                           "taxon_rank", "status", "page", "per_page (max 500)"],
                "taxon_detail": f"{base}/api/taxa/{{id}}",
                "dwca_download": f"{base}/api/dwca",
                "phylogeny": f"{base}/api/phylogeny",
            },
            "license": "CC BY 4.0",
            "source": "https://doi.org/10.1016/j.tree.2019.08.008",
        })

    @app.route("/api/taxa")
    def api_taxa():
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 50, type=int), 500)
        query = _filtered(Taxon.query).order_by(Taxon.scientific_name)
        pag = query.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify({"total": pag.total, "page": pag.page, "per_page": per_page,
                        "pages": pag.pages,
                        "results": [_taxon_to_dict(t) for t in pag.items]})

    @app.route("/api/taxa/<int:taxon_id>")
    def api_taxon(taxon_id):
        return jsonify(_taxon_to_dict(db.get_or_404(Taxon, taxon_id), full=True))

    @app.route("/api/phylogeny")
    def api_phylogeny():
        def node_json(n):
            d = {"id": n["id"], "name": n["name"], "rank": n.get("rank")}
            if n.get("excavate"):
                d["excavate"] = True
            if n.get("children"):
                d["children"] = [node_json(c) for c in n["children"]]
            return d
        return jsonify(node_json(ph.TREE))

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})


# ── Seeding ─────────────────────────────────────────────────────────────────

def seed(app):
    """Populate the catalogue with the representative genera defined in the
    phylogeny backbone (one placeholder species record per genus)."""
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            admin = User(username=os.environ.get("ADMIN_USER", "admin"),
                         email=os.environ.get("ADMIN_EMAIL", "admin@protista.local"),
                         role="admin")
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "admin"))
            db.session.add(admin)
            db.session.commit()
            print(f"Created admin user '{admin.username}'.")
        if Taxon.query.count() > 0:
            return
        n = 0
        for node in ph.iter_nodes():
            genera = node.get("genera") or []
            if not genera:
                continue
            sg = ph.supergroup_of(node["id"])
            hc = ph.higher_classification(node["id"])
            for g in genera:
                n += 1
                db.session.add(Taxon(
                    taxon_id=f"PROT:{node['id']}:{g}",
                    supergroup=sg["name"] if sg else None,
                    clade_id=node["id"],
                    higher_classification=hc,
                    phylum=node["name"] if node.get("rank") == "phylum" else None,
                    genus=g,
                    scientific_name=g,
                    taxon_rank="genus",
                    taxonomic_status="accepted",
                    dataset_name="Protista backbone (Burki et al. 2020; Adl et al. 2019)",
                    references="https://doi.org/10.1016/j.tree.2019.08.008",
                ))
        db.session.commit()
        print(f"Seeded {n} representative genera.")


app = create_app()

if __name__ == "__main__":
    seed(app)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)

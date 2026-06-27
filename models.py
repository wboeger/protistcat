from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Taxon(db.Model):
    __tablename__ = "taxon"

    id = db.Column(db.Integer, primary_key=True)
    taxon_id = db.Column(db.String(255), unique=True, index=True)

    # Higher classification — protists span many kingdoms, so the eukaryote
    # supergroup (sensu Burki et al. 2020) is the top informal rank, and
    # `clade_id` ties each record to a node of the phylogeny backbone.
    supergroup = db.Column(db.String(100), index=True)
    clade_id = db.Column(db.String(100), index=True)        # phylogeny.py node id
    higher_classification = db.Column(db.Text)              # DwC higherClassification

    # names + parentage
    scientific_name = db.Column(db.String(500), index=True)
    taxon_rank = db.Column(db.String(50), index=True)
    parent_name_usage = db.Column(db.String(500))
    parent_name_usage_id = db.Column(db.String(255))

    # full DwC rank ladder (from CTFB mv_planilha_extendida)
    phylum = db.Column(db.String(100), index=True)
    super_class = db.Column(db.String(100))
    class_ = db.Column("class", db.String(100), index=True)
    sub_class = db.Column(db.String(100))
    infra_class = db.Column(db.String(100))
    super_order = db.Column(db.String(100))
    order = db.Column(db.String(100), index=True)
    sub_order = db.Column(db.String(100))
    infra_order = db.Column(db.String(100))
    super_family = db.Column(db.String(100))
    family = db.Column(db.String(100), index=True)
    sub_family = db.Column(db.String(100))
    tribe = db.Column(db.String(100))
    sub_tribe = db.Column(db.String(100))
    genus = db.Column(db.String(100), index=True)
    subgenus = db.Column(db.String(100))
    specific_epithet = db.Column(db.String(100))
    infraspecific_epithet = db.Column(db.String(100))
    scientific_name_authorship = db.Column(db.String(500))
    name_published_in_year = db.Column(db.String(20))

    # nomenclatural / taxonomic status
    taxonomic_status = db.Column(db.String(80), index=True)
    accepted_name_usage = db.Column(db.String(500))
    accepted_name_usage_id = db.Column(db.String(255))
    nomenclatural_status = db.Column(db.String(120))
    modified = db.Column(db.String(60))                     # dcterms:modified (source)
    bibliographic_citation = db.Column(db.Text)
    bibliographic_reference = db.Column(db.Text)

    # distribution / environment
    country = db.Column(db.String(120))
    country_code = db.Column(db.String(10))
    establishment_means = db.Column(db.String(120), index=True)
    endemic_brazil = db.Column(db.String(20), index=True)
    environment = db.Column(db.String(200))
    location_id = db.Column(db.String(255))
    epicontinental_domain = db.Column(db.String(120))
    marine_domain = db.Column(db.String(120))
    life_form = db.Column(db.String(200))
    habitat = db.Column(db.String(500))

    # vernacular
    vernacular_name = db.Column(db.String(500))
    vernacular_name_language = db.Column(db.String(60))
    vernacular_name_locality = db.Column(db.String(255))

    # hosts / symbionts (CTFB-specific)
    animal_host_ids = db.Column(db.Text)
    animal_host_names = db.Column(db.Text)
    vegetal_host_names = db.Column(db.Text)
    animal_symbiont_ids = db.Column(db.Text)
    animal_symbiont_names = db.Column(db.Text)

    # remarks / curation
    occurrence_remarks = db.Column(db.Text)
    internal_remarks = db.Column(db.Text)
    voucher = db.Column(db.Text)
    controlled_bibliography = db.Column(db.Text)
    typology = db.Column(db.String(120))

    dataset_name = db.Column(db.String(500))
    references = db.Column(db.Text)
    extra = db.Column(db.JSON)

    modified_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    modified_by = db.relationship("User", backref="edits")

    audit_logs = db.relationship("AuditLog", backref="taxon", lazy="dynamic")


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="editor")   # editor | admin
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.role == "admin"


class IngestStage(db.Model):
    """Temporary staging area for ingest preview/approval."""
    __tablename__ = "ingest_stage"

    id           = db.Column(db.Integer, primary_key=True)
    session_id   = db.Column(db.String(64), nullable=False, index=True)
    row_index    = db.Column(db.Integer, nullable=False)
    action       = db.Column(db.String(10))     # 'insert' | 'update'
    taxon_id_dwc = db.Column(db.String(255))
    existing     = db.Column(db.JSON)
    incoming     = db.Column(db.JSON)
    diff         = db.Column(db.JSON)
    status       = db.Column(db.String(10), default="pending")  # pending|approved|skipped
    edited       = db.Column(db.JSON)
    created_at   = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    taxon_id = db.Column(db.Integer, db.ForeignKey("taxon.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="audit_logs")
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    changes = db.Column(db.JSON)
    note = db.Column(db.Text)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AcmeNote(models.Model):
    _name = "acme.note"
    _description = "Nota interna"
    _order = "date_deadline, id"

    name = fields.Char(string="Título", required=True)
    description = fields.Text(string="Detalle")
    date_deadline = fields.Date(string="Fecha límite")
    done = fields.Boolean(string="Hecha", default=False)
    is_overdue = fields.Boolean(string="Vencida", compute="_compute_is_overdue")

    @api.depends("date_deadline", "done")
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for note in self:
            note.is_overdue = bool(not note.done and note.date_deadline and note.date_deadline < today)

    @api.constrains("name")
    def _check_name(self):
        for note in self:
            if not (note.name or "").strip():
                raise ValidationError(_("La nota necesita un título."))

    def action_done(self):
        self.write({"done": True})
        return True

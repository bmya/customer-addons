from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAcmeNote(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.context_today(cls.env["acme.note"])
        cls.note = cls.env["acme.note"].create({"name": "Revisar contrato"})

    def test_action_done_marks_the_note_as_done(self):
        self.assertFalse(self.note.done)
        self.note.action_done()
        self.assertTrue(self.note.done)

    def test_empty_title_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.env["acme.note"].create({"name": "   "})

    def test_past_deadline_is_overdue_until_done(self):
        self.note.date_deadline = self.today - timedelta(days=1)
        self.assertTrue(self.note.is_overdue)
        self.note.action_done()
        self.assertFalse(self.note.is_overdue)

    def test_future_or_missing_deadline_is_not_overdue(self):
        self.note.date_deadline = self.today + timedelta(days=1)
        self.assertFalse(self.note.is_overdue)
        self.note.date_deadline = False
        self.assertFalse(self.note.is_overdue)

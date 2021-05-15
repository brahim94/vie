# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from itertools import groupby
from datetime import datetime, timedelta
from odoo.osv import expression

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from datetime import date

_logger = logging.getLogger(__name__)


class CrmClaimCategoryLine(models.Model):
    _name = "crm.claim.category.line"

    name = fields.Char(string="Description", required=True)
    team_id = fields.Many2one('crm.team', 'Business unit')
    claim_category_id = fields.Many2one('crm.claim.category', 'Famille')
    type_demande = fields.Selection([('Reclamation','Réclamation'),('Suggestion','Suggestion')], 'Type de demande', required=True, default="Reclamation", invisible=True)


class CrmTeam(models.Model):
    _inherit = "crm.team"

    member_ids = fields.Many2many('res.users', 'sale_team_id', string='Channel Members')


class ResUsers(models.Model):
    _inherit = "res.users"

    job_id = fields.Many2one('hr.job', string='Hr Job')


class crm_claim_stage(models.Model):
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Etape', required=True, translate=True)
    sequence = fields.Integer('séquence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    team_ids = fields.Many2many('crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Équipe de vente',
                        help="Link between stages and sales teams. When set, this limitate the current stage to the selected sales teams.")
    case_default = fields.Boolean('Commun à toutes les équipes',
                        help="If you check this field, this stage will be proposed by default on each sales team. It will not assign this stage to existing teams.")

    _defaults = {
        'sequence': lambda *args: 1
    }


class crm_magasin(models.Model):
    _name = "crm.magasin"
    _description = "Magasin"

    name = fields.Char('Mgasin', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Business unit', required=True)
    ville = fields.Char('Ville')
    adresse = fields.Char('Adresse')
    user_id = fields.Many2one('res.users', string="Directeur Magasin")


class crm_claim_category(models.Model):
    _name = "crm.claim.category"
    _description = "Category of claim"
    _order = "team_id,name desc"

    name = fields.Char('Nom', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Business unit')
    user_id = fields.Many2one('res.users', 'Responsable')

    notification1 = fields.Integer('Relance en état <Nouvelle> (J)')
    notification2 = fields.Integer('Relance en état <Non Traité>  (J)')

    type_demande = fields.Selection([('Reclamation','Réclamation'),('Suggestion','Suggestion')], 'Type de demande', required=True,default="Reclamation")

    responsable_categorie = fields.Boolean(string="Responsable catégorie")
    directeur_de_magasin = fields.Boolean(string="Directeur de magasin")
    directeur_bu = fields.Boolean(string="Directeur BU")
    equipe_bu = fields.Boolean(string="Equipe BU")

    responsable_categorie1 = fields.Boolean(string="Responsable catégorie")
    directeur_de_magasin1 = fields.Boolean(string="Directeur de magasin")
    directeur_bu1 = fields.Boolean(string="Directeur BU")
    equipe_bu1 = fields.Boolean(string="Equipe BU")
    envoi_immédiat = fields.Boolean(string="Envoi immédiat")


class crm_claim(models.Model):
    _name = "crm.claim"
    _description = "Claim"
    _order = "priority,date desc"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    @api.multi
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team_id = self.env['crm.team'].sudo()._get_default_team_id()
        return self._stage_find(team_id=team_id.id, domain=[('sequence', '=', '1')])

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    id = fields.Integer('ID', readonly=True)
    code = fields.Char(
        string='N° de la réclamation',
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )
    name = fields.Char(compute='_compute_name_rec_sug', string='Objet')
    name_suffix = fields.Char(string='Name Suffix', copy=False)
    active = fields.Boolean('Active',default=lambda *a: 1)
    action_next = fields.Char('Action Suivante')
    date_action_next = fields.Date('Date Action Suivante')

    description = fields.Text('Description',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)
    resolution = fields.Text('Résolution')

    crm_claim_line_id = fields.Many2one('crm.claim.category.line', string="Sous Famille")
    ticket_de_caisse = fields.Binary(attachment=True, string="Ticket de caisse")
    illustration = fields.Binary(attachment=True, string="Illustration")

    create_date = fields.Datetime('Date de création' , readonly=True, default=fields.Datetime.now)
    write_date = fields.Datetime('Date de mise à jour' , readonly=True)
    date_deadline = fields.Date('Date limite',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)
    date_closed = fields.Date('Fermée', readonly=True)
    date = fields.Date('Date réclamation', required=True, track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True, default=fields.Date.context_today)
    categ_id = fields.Many2one('crm.claim.category', 'Famille', required=True, track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)

    user_category_id = fields.Many2one('res.users', 'Responsable Catégorie', track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)

    utm_id = fields.Many2one('utm.medium', 'Canal', required=True, track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)

    priority = fields.Selection([('-1','Low'), ('0','Basse'), ('1','Normale'), ('2','Urgente')], 'Priorité',default='0',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)

    type_demande = fields.Selection([('Reclamation','Réclamation'), ('Suggestion','Suggestion')], 'Type de demande', required=True)


    type_action = fields.Selection([('correction','Action corrective'),('prevention','Action préventive')], 'Type Action',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)

    type_suggestion = fields.Selection([('Iteressante','Itéressante'),('Normale','Normale')], 'Type Suggestion', track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)


    user_id = fields.Many2one('res.users', 'Crée par', track_visibility='always', default=_default_user, readonly=True)
    user_client_id = fields.Many2one('res.users', 'Responsable Service', track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)

    user_fault = fields.Char('Problème',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)
    team_id = fields.Many2one('crm.team', 'Business unit', oldname='section_id', required=True,states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)
    magasin_id = fields.Many2one('crm.magasin', 'Magasin', track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True,required=True)

    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env['res.company']._company_default_get('crm.case'))
    partner_id = fields.Many2one('res.partner', 'Client', required=True, track_visibility='always',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)
    email_cc = fields.Text('Emails des observateurs', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char('E-mail', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char('Téléphone')


    stage_id = fields.Many2one ('crm.claim.stage', 'Etape', track_visibility='onchange',
                domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]")

    state = fields.Selection([('draft','Nouvelle'), ('En cours','En cours'), ('Traite','Traité'), ('Cloture','Clôturé'), ('cancel','Annulé')], 'Etat',default='draft', track_visibility='always')

    cause = fields.Text('Cause première',states={'draft': [('readonly', False)], 'En cours': [('readonly', False)]}, readonly=True)


    @api.depends('name_suffix', 'magasin_id', 'crm_claim_line_id', 'type_demande')
    def _compute_name_rec_sug(self):
        for record in self:
            name = ''
            if record.type_demande == 'Reclamation':
                name += 'Réclamation'
            elif record.type_demande == 'Suggestion':
                name += 'Suggestion'
            name += ('-' + record.magasin_id.name) if record.magasin_id else ''
            name += ('-' + record.crm_claim_line_id.name) if record.crm_claim_line_id else ''
            name += ('-' + record.name_suffix) if record.name_suffix else ''
            record.name = name

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self, email=False):
        if not self.partner_id:
            return {'value': {'email_from': False, 'partner_phone': False}}
        address = self.pool.get('res.partner').browse(self.partner_id)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone}}


    @api.multi
    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id.user_id:
            self.user_client_id = self.team_id.user_id.id


    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id:
            self.user_category_id = self.categ_id.user_id.id or False

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if vals.get('code', '/') == '/':
            vals['code'] = self.env['ir.sequence'].next_by_code('crm.claim')
            vals['name_suffix'] = self.env['ir.sequence'].next_by_code('crm.claim.suffix')
        
        res = super(crm_claim, self).create(vals)
        
        if res.categ_id.type_demande == 'Reclamation' and res.categ_id.envoi_immédiat:
            ## Get na email template
            template = self.env.ref('bi_crm_claim.email_claim_category_creation_template', raise_if_not_found=False)
            assert template._name == 'mail.template'
            
            ## Find users to send an email
            users = []
            if res.categ_id.responsable_categorie:
                users.append(res.categ_id.user_id)
            if res.categ_id.directeur_de_magasin:
                users.append(res.magasin_id.user_id)
            if res.categ_id.directeur_bu:
                users.append(res.team_id.user_id)
            if res.categ_id.equipe_bu:
                for member in res.team_id.member_ids:
                    users.append(member)
            
            ## Email sending to users
            for user in list(set(users)):
                if not user.email:
                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                template.with_context(user=user.id).send_mail(res.id, force_send=True, email_values={'email_to': user.email})
                _logger.info("Claim creation notification has been sent for user <%s> to <%s> for claim <%s>", user.login, user.email, res.code)
        return res

    @api.multi
    def action_cancel(self):
        return self.write({'state': 'cancel'})

    @api.multi
    def action_encours(self):
        return self.write({'state': 'En cours'})

    @api.multi
    def action_traite(self):
        return self.write({'state': 'Traite'})

    @api.multi
    def action_cloture(self):
        return self.write({'state': 'Cloture'})


    @api.multi
    def message_new(self,msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(crm_claim, self).message_new(msg, custom_values=defaults)

    def action_sendmail(self):
        template = self.env.ref('bi_crm_claim.email_claim_category_template', raise_if_not_found=False)
        assert template._name == 'mail.template'

        for category in self.env['crm.claim.category'].search([]):
            users = []
            for claim in self.env['crm.claim'].search([('categ_id', '=', category.id), ('team_id', '=', category.team_id.id), ('state', 'in', ('draft', 'En cours'))]):
                # For Reclamations
                if claim.type_demande == 'Reclamation':
                    if claim.state == 'draft' and claim.date + relativedelta(days=category.notification1) <= date.today():
                        if category.responsable_categorie:
                            users.append(category.user_id)
                        if category.directeur_de_magasin:
                            users.append(claim.magasin_id.user_id)
                        if category.directeur_bu:
                            users.append(claim.team_id.user_id)
                        if category.equipe_bu:
                            for member in claim.team_id.member_ids:
                                users.append(member)

                    elif claim.state == 'En cours' and claim.date + relativedelta(days=category.notification2) <= date.today():
                        if category.responsable_categorie:
                            users.append(category.user_id)
                        if category.directeur_de_magasin:
                            users.append(claim.magasin_id.user_id)
                        if category.directeur_bu:
                            users.append(claim.team_id.user_id)
                        if category.equipe_bu:
                            for member in claim.team_id.member_ids:
                                users.append(member)

                # For Suggestions
                elif claim.type_demande == 'Suggestion':
                    if claim.state == 'draft' and claim.date + relativedelta(days=category.notification1) <= date.today():
                        if category.responsable_categorie:
                            users.append(category.user_id)
                        if category.directeur_de_magasin:
                            users.append(claim.magasin_id.user_id)
                        if category.directeur_bu:
                            users.append(claim.team_id.user_id)
                        if category.equipe_bu:
                            for member in claim.team_id.member_ids:
                                users.append(member)

                    elif claim.state == 'En cours' and claim.date + relativedelta(days=category.notification2) <= date.today():
                        if category.responsable_categorie:
                            users.append(category.user_id)
                        if category.directeur_de_magasin:
                            users.append(claim.magasin_id.user_id)
                        if category.directeur_bu:
                            users.append(claim.team_id.user_id)
                        if category.equipe_bu:
                            for member in claim.team_id.member_ids:
                                users.append(member)

                for user in list(set(users)):
                    if not user.email:
                        raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
                    template.with_context(user=user.id).send_mail(claim.id, force_send=True, email_values={'email_to': user.email})
                    _logger.info("Claim notification has been sent for user <%s> to <%s> for claim <%s>", user.login, user.email, claim.code)


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
            domain = criteria_operator + [('mobile', '=ilike', name + '%'), ('name', operator, name)]
        group_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return self.browse(group_ids).name_get()

    @api.multi
    def _claim_count(self):
        for claim in self:
            claim_ids = self.env['crm.claim'].search([('partner_id','=',claim.id)])
            claim.claim_count = len(claim_ids)

    @api.multi
    def claim_button(self):
        self.ensure_one()
        return {
            'name': 'Reclamations/Suggestions',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crm.claim',
            'domain': [('partner_id', '=', self.id)],
        }

    claim_count = fields.Integer(string='# Reclamations/Suggestions',compute='_claim_count')



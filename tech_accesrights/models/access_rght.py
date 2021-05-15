from odoo import fields, api, models, _

class Magasin(models.Model): 
    _inherit = "crm.magasin"

    id_magasin = fields.Char(string="ID Magasin", required="False")
    email_sav = fields.Char(string='E-mail SAV')
    
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (id_magasin)',
         'id magasin must be unique.')
    ]

class ResUsers(models.Model):
    _inherit = "res.users"

    all_stores = fields.Boolean(string="Tous les magasins")
    business_unit_ids = fields.Many2many('crm.team', 'team_user2_rel', 'user_id', 'team_id', string='BUs')
    magasin_ids = fields.Many2many('crm.magasin', 'magasins_user2_rel', 'user_id', 'magasin_id', string='Magasins associés')


class Ticket(models.Model):
    _inherit = "ticket.ticket"

    business_unit = fields.Many2one('crm.team', string='BU')
    magasin = fields.Many2one('crm.magasin', string='Magasin')
  

    @api.onchange('invoice_id')
    def onchange_invoice_id_article_id(self):
        if self.invoice_id.article:
                for article_code in self.env['articles.parameter'].search([('code_ean', '=', self.invoice_id.article)]):
                        self.date_achat = self.invoice_id.date
                        self.article_id = article_code.id
                        self.n_serie = self.invoice_id.serial_number
                        self.fournisseur = article_code.fournisseur.id
                        ticket_ids = self.env['ticket.ticket'].search([('invoice_id.name', '=', self.invoice_id.name)])
                        self.ticket_history_ids = ticket_ids.ids if ticket_ids else False
                        self.garantie = article_code.garantie
                        self.duree = article_code.duree
                        self.article_code = article_code.code_ean
        

            
    @api.onchange('invoice_id')
    def onchange_invoice_id2(self):
        
        self.magasin = self.invoice_id.magasin_id.id
        self.business_unit = self.invoice_id.magasin_id.team_id.id


class Factures(models.Model):
    _inherit = "factures.factures"

    def _get_default_magasin(self):
	    # DO YOU REALLY HAVE THE PARTNER WHICH NAME IS city??
	    if self.id_magas_in: 
	    	return self.env['crm.magasin'].search([('id_magasin', '=', self.id_magas_in)], limit=1).id_magasin
	    
    magasin_id = fields.Many2one('crm.magasin', string='Magasin',default=_get_default_magasin)
    
    @api.onchange('id_magas_in')
    def onchange_client_id(self):
        magasin_id = self.env['crm.magasin'].search([('id_magasin','=',self.id_magas_in)])
        if magasin_id:
                for magasin in magasin_id:
                        self.magasin_id = magasin.id
        		
        		
        		
class partner(models.Model): 
    _inherit = "res.partner"

    def _get_default_magasin(self):
        if self.env.user.magasin_ids:
        	return self.env.user.magasin_ids[0]
        
    magasin_id = fields.Many2one('crm.magasin', string='Magasin', default=_get_default_magasin)
    sms_authorisation = fields.Boolean('SMS AUTORISÉ ?')
    
    @api.multi
    @api.onchange('magasin_id')
    def onchange_magasin_id(self):
    	self.business_unit_id = self.magasin_id.team_id.id
     
    business_unit_id = fields.Many2one('crm.team', string='BU')
   
   

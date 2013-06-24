
import time
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare

class venta_credito(osv.osv):    
    _name = 'venta.credito'
              
    def get_saldo(self, cr, uid, ids, context=None):
        saldo = valor = val = va = ent = entrada= 0.0
        values={}
        #import pdb
        #pdb.set_trace()
        if context.get("entrada"):             
            ent=context.get("entrada")
        if context.get("valor"):
            va=context.get("valor")          
        if context is None:
            return True
        for form in self.browse(cr, uid, ids, context=context):
            entrada=form.entrada
            valor=form.valor              
            if form.cobros_ids:
                for line in form.cobros_ids:
                    val += line.abono
        if va != valor and va!=0.0:
            valor=va
        if ent != entrada and ent!=0.0:
            entrada=ent    
        saldo = valor -val- entrada
        if saldo < 0:
            saldo=-999999999;
        values = {'saldo':saldo}
        return {'value':values}
    
    def get_name(self, cr, uid, ids, context):
        #import pdb
        #pdb.set_trace()
        res = {}
        value={}
        if context is None:
            context = {}
        if context.get("fecha_venta"):
            res['fecha_venta'] = context.get("fecha_venta")
        if context.get("numero"):
            res['numero'] = context.get("numero")
        if context.get("cliente_id"):
            res['cliente_id'] = context.get("cliente_id")
        cliente = self.pool.get('res.partner').browse(cr,uid,res['cliente_id'] ,context)
        val = ""
        if cliente:
            if res['numero'] and res['fecha_venta']:
                val= res['numero'] + "|" + cliente.name + "|" +  res['fecha_venta']
            elif not res['numero'] and res['fecha_venta']:
                val = cliente.name + "|" + res['fecha_venta']
            elif not res['fecha_venta'] and res['numero'] :
                val =res['numero'] + "|" +  cliente.name
            value['name'] = val
        return value
   
    def on_change_cliente(self, cr, uid, ids,cliente_id,context=None):
        #import pdb
        #pdb.set_trace()
        desc=self.get_name(cr, uid, ids, context)
        values = {
                  'name':None,
                  'es_venta':False,
                  'direccion':None,
                  'telefono':None
                  }
        if context is None:
            context = {}
        if context.get("es_venta"):
            values['es_venta'] = True
        cliente = self.pool.get('res.partner').browse(cr,uid,cliente_id,context)
        values['direccion'] = cliente.street 
        values['telefono'] = cliente.phone
        if desc:
            values['name']=desc['name']
        return {'value':values}
    
    def on_change_garante(self, cr, uid, ids,cliente_id,context=None):
        cliente = self.pool.get('res.partner').browse(cr,uid,cliente_id,context)
        values = {'direccion2':cliente.street, 'telefono2':cliente.phone}
        return {'value':values} 
    
    def _check_paid(self, cr, uid, ids, prop, unknow_none, context):
        form = self.browse(cr, uid, ids[0])
        return True
    
    def _get_saldo(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        values={}
        val = saldo = 0.0
        for form in self.browse(cr, uid, ids, context=context):
            if form.cobros_ids:
                for line in form.cobros_ids:
                    val += line.abono
            saldo = form.valor - val - form.entrada
            res[form.id] = saldo
            values['saldo1']=saldo # Para el tree
        if values:
            self.write(cr, uid, ids, values)
        return res
    
    def _get_name(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = ""
        for form in self.browse(cr, uid, ids, context=context):
            if form.numero and form.cliente_id.name:
                val= form.numero + "|" + form.cliente_id.name + "|" + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + "|" + form.fecha_venta
            elif not form.numero and form.cliente_id.name:
                val = form.cliente_id.name + "|" + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + "|" + form.fecha_venta
            res[form.id] = val
        return res

    def onChange_pedido(self, cr, uid, ids, comprobante_id, context=None):
        values={}
        comprobant=self.pool.get('stock.picking.in').browse(cr, uid,comprobante_id, context)
        if (comprobant):            
            values['cliente_id']=comprobant.partner_id.name
            values['direccion']=comprobant.partner_id.street
            values['telefono']=comprobant.partner_id.phone
        return {'value': values} or False
    
    def onChange_venta(self, cr, uid, ids, comprobante_id, context=None):
        values={}
        comprobant=self.pool.get('stock.picking.out').browse(cr, uid,comprobante_id, context)
        if (comprobant):            
            values['cliente_id']=comprobant.partner_id.name
            values['direccion']=comprobant.partner_id.street
            values['telefono']=comprobant.partner_id.phone
        return {'value': values} or False

    _columns = {
                #'name':fields.char('Nombre', size=512, help="Nombre de la venta realizada."),
                #'name':fields.function(_get_name, string='Descripcion', type='char', help="Nombre del credito"),
                'name':fields.char('Venta', size=512, help="Identificador de la venta realizada."),
                'numero':fields.char('Codigo', size=512, help="Identificador de la venta realizada."),
                #'cliente_id':fields.char('Cliente', size=64, required = True, help="Cliente al que se le da el credito"),
                'cliente_id':fields.many2one('res.partner', 'Cliente', required = True, help="Cliente al que se le da el credito"),  
                'direccion':fields.char('Direccion', size=512, help="Direccion del cliente."),
                'telefono':fields.char('Telefono', size=512, help="Telefono del Cliente."),
                'cart_cl':fields.char('C/L', size=512, help="Telefono del Cliente."),
                'garante_id':fields.many2one('res.partner', 'Garante', help="Garante del credito de la venta."),
                'direccion2':fields.char('Direccion', size=512, help="Direccion del garante."),
                'telefono2':fields.char('Telefono', size=512, help="Telefono del garante."),
                'entrada':fields.float('Entrada', help="Valor que se dio de entrada."),
                'fecha_venta':fields.date('Fecha', help="Dia en que se realiza la venta"),
                'producto_id':fields.many2one('product.product', 'Articulo', help="Articulo que se incluye en la venta."),
                'valor':fields.float('Valor', help="Valor del Articulo vendido."),
                'saldo':fields.function(_get_saldo, string='Saldo', type='float', help="Valor pendiente a pagar"),
                'saldo1':fields.float('Saldo', help="Saldo pendiente."),
                #'pedidos':fields.many2one('stock.picking.in', 'Compra Ref', help="Pedido de compra No"),
                #'ventas':fields.many2one('stock.picking.out', 'Venta Ref', help="Pedido de venta No"),
                'pedidos':fields.char('Compra Ref',size=64, help="Pedido de compra No"),
                'ventas':fields.char('Venta Ref',size=64, help="Pedido de venta No"),
                'cobros_ids':fields.one2many('venta.cobro','venta_credito_id','Lineas de Cobros'),
                'es_venta':fields.boolean('Es venta'),
                }
    
    _defaults = {
        'fecha_venta': lambda *a: time.strftime('%Y-%m-%d'),
    }
venta_credito()


class venta_cobro(osv.osv):
    _name = 'venta.cobro'

    def get_total(self, cr, uid, ids, abono, context):
        venta_id=0;
        tree= self.browse(cr, uid, ids, context=context)
        if not context:
            context={}
        else:
            venta_id= context.get('venta_id')
            cobro_id= context.get('cobro_id')
        values={}
        val={}
        import pdb
        pdb.set_trace()
        venta = self.pool.get('venta.credito').browse(cr,uid,venta_id,context)
        inv_obj = self.pool.get('venta.credito')
        values['total']=venta.saldo
        saldo = values['total'] - abono
        if saldo < 0:
            saldo=-999999999;
        else:
            values['saldo']=saldo
            val['saldo1']=saldo
            inv_obj.write(cr, uid, venta_id, val, context=context)
            self.write(cr, uid, ids, values, context)
        return {'value':values}
        
    _columns = {
                'venta_credito_id':fields.many2one('venta.credito', 'Venta', required=1, ondelete='cascade'),
                'abono': fields.float('Abono', help="Valor que se abona a la deuda."),
                'interes': fields.float('Interes', help="Registro de interes."),
                'total': fields.float('Total', help="Total."),
                'saldo': fields.float('Saldo', help="Saldo pendiente."),
                'fecha_cobro':fields.date('Fecha', select=True, help="Dia en que se realiza el pago"),
                }
    
    _defaults = {
        'fecha_cobro': lambda *a: time.strftime('%Y-%m-%d'),
    }
venta_cobro()


class cobro_wizard(osv.osv_memory):
    _name = 'cobro.wizard'
    
    def get_total(self, cr, uid, ids, venta_id, context=None):
        saldo = valor = entrada =abono= 0.0
        values={}
        val={}
        venta = self.pool.get('venta.credito').browse(cr,uid,venta_id,context)
        inv_obj = self.pool.get('venta.credito')
        values['total']=venta.saldo
        if context: 
            if context.get("abono"):             
                abono=context.get("abono")
            if context.get("interes"):
                valor=context.get("interes")
            saldo = values['total'] - abono
            if saldo < 0:
                saldo=-999999999;
            else:
                values['saldo']=saldo
                val['saldo1']=saldo
                #import pdb
               # pdb.set_trace()
                inv_obj.write(cr, uid, venta_id, val, context=context)
        return values
    
    _columns = {
                'venta_credito_id':fields.many2one('venta.credito', 'Venta', required=1, ondelete='cascade'),
                'abono': fields.float('Abono', help="Valor que se dio de entrada."),
                'interes': fields.float('Interes', help="Valor que se dio de entrada."),
                'fecha_cobro':fields.date('Fecha', select=True, help="Dia en que se realiza la venta"),
                }
    
    _defaults = {
        'fecha_cobro': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def do_cobro(self, cr, uid, ids, context=None):
        cobro_pool =  self.pool.get('venta.cobro')
        res={}
        #import pdb
        #pdb.set_trace()
        if context:
            if context.get("fecha_cobro"):
                res['fecha_cobro'] = context.get("fecha_cobro")
            if context.get("interes"):
                res['interes'] = context.get("interes")
            else:
                res['interes']=0.0
            if context.get("abono"):
                res['abono'] = context.get("abono")
            else:
                res['abono']=0.0
            if context.get("venta_credito_id"):
                res['venta_credito_id'] = context.get("venta_credito_id")
            val=self.get_total(cr, uid, ids, res['venta_credito_id'], context)
            for form in self.browse(cr, uid, ids, context=context):
                cobro_pool.create(cr, uid, {
                                            'fecha_cobro': res['fecha_cobro'],
                                            'total': val['total'],
                                            'abono': res['abono'],
                                            'interes': res['interes'] ,
                                            'saldo':val['saldo'],
                                            'venta_credito_id': res['venta_credito_id'],           
                            })
        return True
    
cobro_wizard()


class venta_credito_wizard(osv.osv_memory):
    
    _name = 'venta.credito.wizard'
    
    def get_saldo(self, cr, uid, ids, context=None):
        saldo = valor = entrada= 0.0
        values={}
        if context.get("entrada"):             
            entrada=context.get("entrada")
        if context.get("valor"):
            valor=context.get("valor")
        if context is None:
            return True 
        saldo = valor - entrada
        if saldo < 0:
            saldo=-999999999;
        values = {'saldo':saldo}
        return {'value':values}
    
    def _get_saldo(self, cr, uid, ids, prop, unknow_none, context):
        val = 0.0
        res = {}
        saldo = 0.0
        for form in self.browse(cr,uid,ids):
            res[form.id] = form.valor - form.entrada
        return res
    
    def get_name(self, cr, uid, ids, context):
        res = {}
        value={}
        if context is None:
            context = {}
        if context.get("fecha_venta"):
            res['fecha_venta'] = context.get("fecha_venta")
        if context.get("numero"):
            res['numero'] = context.get("numero")
        if context.get("cliente_id"):
            res['cliente_id'] = context.get("cliente_id")
        cliente = self.pool.get('res.partner').browse(cr,uid,res['cliente_id'] ,context)
        val = ""
        if cliente:
            if res['numero'] and res['fecha_venta']:
                val= res['numero'] + "|" + cliente.name + "|" +  res['fecha_venta']
            elif not res['numero'] and res['fecha_venta']:
                val = cliente.name + "|" + res['fecha_venta']
            elif not res['fecha_venta'] and res['numero'] :
                val =res['numero'] + "|" +  cliente.name
            value['name'] = val
        return value
        
    def _get_name(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = ""
        for form in self.browse(cr, uid, ids, context=context):
            if form.numero and form.cliente_id.name:
                val= form.numero + "|" + form.cliente_id.name + "|" + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + "|" + form.fecha_venta
            elif not form.numero and form.cliente_id.name:
                val = form.cliente_id.name + "|" + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + "|" + form.fecha_venta
            res[form.id] = val
        return res
    
    def on_change_cliente(self, cr, uid, ids,cliente_id,context=None):
        #import pdb
        #pdb.set_trace()
        desc=self.get_name(cr, uid, ids, context)
        values = {
                  'name':None,
                  'direccion':None,
                  'telefono':None
                  }
        cliente = self.pool.get('res.partner').browse(cr,uid,cliente_id,context)
        values['direccion'] = cliente.street 
        values['telefono'] = cliente.phone
        if desc:
            values['name']=desc['name']
        return values
    
    def on_change_garante(self, cr, uid, ids,garante_id,context=None):
        garante = self.pool.get('res.partner').browse(cr,uid,garante_id,context)
        values = {'direccion2':garante.street, 'telefono2':garante.phone}
        return values 
    
    _columns = {
                #'name':fields.function(_get_name, string='Descripcion', type='char', help="Nombre del credito"),
                'name':fields.char('Descripcion', size=120, help="Identificador de la venta realizada."),
                'numero':fields.char('Codigo', size=64, help="Identificador de la venta realizada."),
                'cliente_id':fields.many2one('res.partner', 'Cliente',required = True, help="Cliente al que se le da el credito"),
                #'name':fields.function(_get_name, string='Nombre', type='char', help="Nombre del credito"),
                #'numero':fields.char('Numero', size=512, help="Identificador de la venta realizada."),
                'cliente_id':fields.many2one('res.partner', 'Cliente', required = True, help="Cliente al que se le da el credito"),
                'garante_id':fields.many2one('res.partner', 'Garante', help="Garante del credito de la venta."),
                'entrada':fields.float('Entrada', help="Valor que se dio de entrada."),
                'fecha_venta':fields.date('Fecha', select=True, help="Dia en que se realiza la venta"),
                'producto_id':fields.many2one('product.product', 'Articulo', help="Articulo que se incluye en la venta."),
                'valor':fields.float('Valor', help="Valor del Articulo vendido."),
                'saldo':fields.function(_get_saldo, string='Saldo', type='float'),
                }
    
    _defaults = {
        'fecha_venta': lambda *a: time.strftime('%Y-%m-%d'),
    }  
    
    def do_venta(self, cr, uid, ids, context=None):
        venta_pool =  self.pool.get('venta.credito')
        #import pdb
        #pdb.set_trace()     
        res={}
        if context:
            if context.get("fecha_venta"):
                res['fecha_venta'] = context.get("fecha_venta")
            if context.get("numero"):
                res['numero'] = context.get("numero")
            if context.get("cliente_id"):
                res['cliente_id'] = context.get("cliente_id")
            if context.get("garante_id"):
                res['garante_id'] = context.get("garante_id")             
            values=self.on_change_cliente(cr, uid, ids, res['cliente_id'], context)
            values2=self.on_change_garante(cr, uid, ids, res['garante_id'], context)
            formularios=self.browse(cr, uid, ids, context=context) 
            for form in formularios: 
                venta_pool.create(cr, uid, {
                                            'es_venta':1,
                                            'numero':res['numero'],
                                            'name':values['name'],
                                            'cliente_id':res['cliente_id'],
                                            'direccion':values['direccion'],
                                            'telefono': values['telefono'],   
                                            'garante_id':res['garante_id'],
                                            'direccion2':values2['direccion2'],
                                            'telefono2': values2['telefono2'],
                                            'producto_id':form.producto_id.id,
                                            'valor':form.valor,
                                            'entrada':form.entrada,
                                            'saldo':form.saldo,
                                            'saldo1':form.saldo,
                                            'fecha_venta':res['fecha_venta'],
                                            })
        return True
    
venta_credito_wizard()

class pago_wizard(osv.osv_memory):
    
    _name = 'pago.wizard'
    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
        
    def get_total(self, cr, uid, ids, venta_id, context=None):
        saldo  = abono= 0.0
        values={}
        val={}
        venta = self.pool.get('venta.credito').browse(cr,uid,venta_id,context)
        inv_obj = self.pool.get('venta.credito')
        values['total']=venta.saldo
        if context: 
            if context.get("abono"):             
                abono=context.get("abono")
            saldo = values['total'] - abono
            if saldo < 0:
                saldo=-999999999;
            else:
                values['saldo']=saldo
                val['saldo1']=saldo
                inv_obj.write(cr, uid, venta_id, val, context=context)
        return values
    
    _columns = {
                'venta_credito_id':fields.many2one('venta.credito', 'Venta', required=1, ondelete='cascade'),
                'abono': fields.float('Abono', help="Valor que se dio de entrada."),
                'interes': fields.float('Interes', help="Valor que se dio de entrada."),
                'fecha_cobro':fields.date('Fecha', select=True, help="Dia en que se realiza la venta"),
                }
    
    _defaults = {
        'fecha_cobro': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def do_pago(self, cr, uid, ids, context=None):
        pago_pool =  self.pool.get('venta.cobro')
        res={}
        #import pdb
        #pdb.set_trace()
        if context:
            if context.get("fecha_cobro"):
                res['fecha_cobro'] = context.get("fecha_cobro")
            if context.get("interes"):
                res['interes'] = context.get("interes")
            else:
                res['interes']=0.0
            if context.get("abono"):
                res['abono'] = context.get("abono")
            else:
                res['abono']=0.0
            if context.get("venta_credito_id"):
                res['venta_credito_id'] = context.get("venta_credito_id")
            val=self.get_total(cr, uid, ids, res['venta_credito_id'], context)
            for form in self.browse(cr, uid, ids, context=context):
                pago_pool.create(cr, uid, {
                                            'fecha_cobro': res['fecha_cobro'],
                                            'total': val['total'],
                                            'abono': res['abono'],
                                            'interes': res['interes'] ,
                                            'saldo':val['saldo'],
                                            'venta_credito_id': res['venta_credito_id'],           
                            })                
                
        return True
cobro_wizard()


class compra_credito_wizard(osv.osv_memory):
    
    _name = 'compra.credito.wizard'
    
    def get_saldo(self, cr, uid, ids, context=None):
        saldo = valor = entrada= 0.0
        values={}
        if context.get("entrada"):             
            entrada=context.get("entrada")
        if context.get("valor"):
            valor=context.get("valor")
        if context is None:
            return True 
        saldo = valor - entrada
        if saldo < 0:
            saldo=-999999999;
        values = {'saldo':saldo}
        return {'value':values}    
    
    def _get_saldo(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        saldo = 0.0
        for form in self.browse(cr,uid,ids):
            res[form.id] = form.valor - form.entrada
        return res
    
    def _get_name(self, cr, uid, ids, prop, unknow_none, context):
        res = {}
        val = ""
        for form in self.browse(cr, uid, ids, context=context):
            if form.numero and form.cliente_id.name:
                val= form.numero + "|" + form.cliente_id.name + "|" + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + "|" + form.fecha_venta
            elif not form.numero and form.cliente_id.name:
                val = form.cliente_id.name + "|" + form.fecha_venta
            elif form.numero and not form.cliente_id.name:
                val = form.numero + "|" + form.fecha_venta
            res[form.id] = val
        return res

    def get_name(self, cr, uid, ids, context):
        res = {}
        value={}
        if context is None:
            context = {}
        if context.get("fecha_venta"):
            res['fecha_venta'] = context.get("fecha_venta")
        if context.get("numero"):
            res['numero'] = context.get("numero")
        if context.get("cliente_id"):
            res['cliente_id'] = context.get("cliente_id")
        cliente = self.pool.get('res.partner').browse(cr,uid,res['cliente_id'] ,context)
        val = ""
        if cliente:
            if res['numero'] and res['fecha_venta']:
                val= res['numero'] + "|" + cliente.name + "|" +  res['fecha_venta']
            elif not res['numero'] and res['fecha_venta']:
                val = cliente.name + "|" + res['fecha_venta']
            elif not res['fecha_venta'] and res['numero'] :
                val =res['numero'] + "|" +  cliente.name
            value['name'] = val
        return value        
    
    def on_change_cliente(self, cr, uid, ids,cliente_id,context=None):
        #import pdb
        #pdb.set_trace()
        desc=self.get_name(cr, uid, ids, context)
        values = {
                  'name':None,
                  'direccion':None,
                  'telefono':None
                  }
        cliente = self.pool.get('res.partner').browse(cr,uid,cliente_id,context)
        values['direccion'] = cliente.street 
        values['telefono'] = cliente.phone
        if desc:
            values['name']=desc['name']
        return values
        
    _columns = {
                'name':fields.char('Descripcion', size=120, help="Nombre de la venta realizada."),
                #'name':fields.function(_get_name, string='Descripcion', type='char', help="Nombre del credito"),
                'numero':fields.char('Codigo', size=512, help="Identificador de la venta realizada."),
                'cliente_id':fields.many2one('res.partner', 'Cliente', required = True, help="Cliente al que se le da el credito"),
                'garante_id':fields.many2one('res.partner', 'Garante', help="Garante del credito de la venta."),
                'entrada':fields.float('Entrada', help="Valor que se dio de entrada."),
                'fecha_venta':fields.date('Fecha', select=True, help="Dia en que se realiza la venta"),
                'producto_id':fields.many2one('product.product', 'Articulo', help="Articulo que se incluye en la venta."),
                'valor':fields.float('Valor', help="Valor del Articulo vendido."),
                'saldo':fields.function(_get_saldo, string='Saldo', type='float'),
                }
    
    _defaults = {
        'fecha_venta': lambda *a: time.strftime('%Y-%m-%d'),
    }  
    
    def do_compra(self, cr, uid, ids, context=None):
        venta_pool =  self.pool.get('venta.credito')
        #import pdb
        #pdb.set_trace()
        res={}
        if context:
            if context.get("fecha_venta"):
                res['fecha_venta'] = context.get("fecha_venta")
            if context.get("numero"):
                res['numero'] = context.get("numero")
            if context.get("cliente_id"):
                res['cliente_id'] = context.get("cliente_id")
            values=self.on_change_cliente(cr, uid, ids, res['cliente_id'], context)    
            for form in self.browse(cr, uid, ids, context=context):
                venta_pool.create(cr, uid, {
                                            'numero':res['numero'],
                                            'name':values['name'],
                                            'cliente_id':res['cliente_id'],                                                                                
                                            'fecha_venta':res['fecha_venta'],
                                            'direccion':values['direccion'],
                                            'telefono':values['telefono'],    
                                            'producto_id':form.producto_id.id,
                                            'valor':form.valor,
                                            'entrada':form.entrada,
                                            'saldo':form.saldo,
                                            'saldo1':form.saldo,
                                            })
        return True
    
compra_credito_wizard()


#<!-- SOLO PROBANDOLE AL JORCH LO Q DIGO --> 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
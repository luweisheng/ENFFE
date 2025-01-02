# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # 添加采购单数据
    def _add_purchase_data(self, product_id, po_data, price_id, date, product_qty, main_bom_id, bom_id, origin):
        partner_id = price_id.name
        payment_term_id = partner_id.payment_term_id.id
        trade_term_id = partner_id.trade_term_id.id
        user_id = partner_id.user_id.id
        po_line_key = str(product_id.id) + '_' + str(price_id.id)
        if partner_id not in po_data:
            po_data[partner_id] = {'supplier_id': partner_id.id,
                                   'tax_included': partner_id.tax_included,
                                   'tax_rate': partner_id.tax_rate,
                                   'origin': origin,
                                   'date_order': date,
                                   'user_id': user_id,
                                   'payment_term_id': payment_term_id,
                                   'trade_term_id': trade_term_id,
                                   'sale_order_id': self.id,
                                   'contract_no': self.contract_no,
                                   'order_line': {po_line_key: {
                                       'product_id': product_id.id,
                                       'supplier_id': partner_id.id,
                                       'price_id': price_id.id,
                                       'product_qty': product_qty,
                                       'is_auto': True,
                                       'price_unit': price_id.price,
                                       'order_line_list': [(0, 0, {
                                           'product_id': product_id.id,
                                           'supplier_id': partner_id.id,
                                           'price_id': price_id.id,
                                           'product_qty': product_qty,
                                           'is_auto': True,
                                           'price_unit': price_id.price,
                                           'main_bom_id': main_bom_id.id if main_bom_id else None,
                                           'bom_id': bom_id.id if bom_id else None,
                                       })]
                                   }}
                                   }

        else:
            # 判断该产品是否存在采购订单行，如果存在则累加数量

            order_line = po_data[partner_id]['order_line']
            if po_line_key not in order_line:
                po_data[partner_id]['order_line'][po_line_key] = {
                    'product_id': product_id.id,
                    'supplier_id': partner_id.id,
                    'price_id': price_id.id,
                    'product_qty': product_qty,
                    'price_unit': price_id.price,
                    'is_auto': True,
                    'order_line_list': []
                }
            else:
                po_data[partner_id]['order_line'][po_line_key]['product_qty'] += product_qty
            po_data[partner_id]['order_line'][po_line_key]['order_line_list'].append((0, 0, {
                'product_id': product_id.id,
                'supplier_id': partner_id.id,
                'price_id': price_id.id,
                'product_qty': product_qty,
                'price_unit': price_id.price,
                'is_auto': True,
                'main_bom_id': main_bom_id.id,
                'bom_id': bom_id.id
            }))
            if origin not in po_data[partner_id]['origin']:
                po_data[partner_id]['origin'] += ',' + origin

    # 添加生产单数据
    def _add_production_data(self, bom_id, mo_data, sale_qty, date, po_data, main_bom_id, origin, sale_line_id):
        # 查询此制造产品是否存在mo_data
        mo_key = bom_id.product_id.id
        if mo_key in mo_data:
            # 生产数累加
            mo_data[mo_key]['product_qty'] += sale_qty
            # 生产明细生产数累加
            for mo_line in mo_data[mo_key]['production_line']:
                add_qty = sale_qty * mo_line['unit_factor']
                mo_line['product_qty'] += add_qty
                mo_line['order_qty'] += add_qty
                # origin增加
                if origin not in mo_data[mo_key]['origin']:
                    mo_data[mo_key]['origin'] += ',' + origin
                product_id = mo_line['product_id']
                price_id = mo_line['price_id']
                # 添加采购数据
                self._add_purchase_data(product_id, po_data, price_id, date, add_qty, main_bom_id, bom_id, origin)
        else:
            mo_name = self.env['ir.sequence'].next_by_code('mrp.production')
            origin = mo_name
            mo_data[mo_key] = {
                'name': mo_name,
                'origin': origin,
                'product_id': mo_key,
                'order_qty': sale_qty,
                'product_qty': sale_qty,
                'bom_id': bom_id.id,
                'sale_order_id': self.id,
                'contract_no': self.contract_no,
                'plan_start_date': date,
                'state': 'confirmed',
                'factory_id': sale_line_id.factory_id.id,
                'production_line': {}
            }
            for mo_line in bom_id.bom_line:
                add_qty = sale_qty * mo_line.product_qty
                mo_data[mo_key]['production_line'][mo_line.id] = {
                    'product_id': mo_line.product_id.id,
                    'product_qty': add_qty,
                    'unit_factor': mo_line.product_qty,
                    'supplier_id': mo_line.price_id.name.id,
                    'price_id': mo_line.price_id.id,
                    'bom_line_id': mo_line.id,
                    'bom_note': mo_line.note
                }
                if mo_line.product_id.bom_id:
                    continue
                self._add_purchase_data(mo_line.product_id, po_data, mo_line.price_id, date, add_qty,
                                        main_bom_id, bom_id, mo_name)
        return origin

    # 遍历BOM明细
    def _check_bom_line(self, bom_id, sale_line_id, mo_data, po_data, date, sale_qty, main_bom_id, origin):
        origin = self._add_production_data(bom_id, mo_data, sale_qty, date, po_data, main_bom_id, origin, sale_line_id)
        for line in bom_id.bom_line:
            bom_id = line.product_id.bom_id
            # 判断产品是否有BOM
            if bom_id:
                sale_qty = sale_qty * line.product_qty
                self._check_bom_line(bom_id, sale_line_id, mo_data, po_data, date, sale_qty, main_bom_id, origin)

    # 判断产品是否有BOM
    def _check_product_bom(self, product_id, sale_line_id, mo_data, po_data, date, sale_qty):
        origin = self.name
        bom_id = product_id.bom_id
        if bom_id:
            self._check_bom_line(bom_id, sale_line_id, mo_data, po_data, date, sale_qty, bom_id, origin)
        else:
            price_id = sale_line_id.price_id
            bom_id = None
            self._add_purchase_data(product_id, po_data, price_id, date, sale_qty, bom_id, bom_id, origin)

    # 下单逻辑
    def action_done(self):
        if self.order_type == 'sell':
            return super(SaleOrder, self).action_done()
        mo_data = {}
        po_data = {}
        # 获取当前时间
        date = fields.Datetime.now()
        # 逻辑处理
        for line in self.order_line:
            sale_qty = line.product_uom_qty
            # 判断产品是否有BOM
            self._check_product_bom(line.product_id, line, mo_data, po_data, date, sale_qty)

        # 生成生产单
        for key, value in mo_data.items():
            production_line = [(0, 0, line) for line in value['production_line'].values()]
            value['production_line'] = production_line
            self.env['mrp.production'].create(value)
        # 生成采购单
        for key, value in po_data.items():
            order_line = [(0, 0, line) for line in value['order_line'].values()]
            value['order_line'] = order_line
            self.env['purchase.order'].create(value)
        return super(SaleOrder, self).action_done()

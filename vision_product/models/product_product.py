# -*- coding: utf-8 -*-
import logging
from decorator import decorator

from odoo import models, fields, api, _
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


def assert_log_admin_access(method):
    """Decorator checking that the calling user is an administrator, and logging the call.

    Raises an AccessDenied error if the user does not have administrator privileges, according
    to `user._is_admin()`.
    """
    def check_and_log(method, self, *args, **kwargs):
        user = self.env.user
        origin = request.httprequest.remote_addr if request else 'n/a'
        log_data = (method.__name__, self.sudo().mapped('display_name'), user.login, user.id, origin)
        if not self.env.is_admin():
            _logger.warning('DENY access to module.%s on %s to user %s ID #%s via %s', *log_data)
            raise AccessDenied()
        _logger.info('ALLOW access to module.%s on %s to user %s #%s via %s', *log_data)
        return method(self, *args, **kwargs)
    return decorator(check_and_log, method)


class VisionModulePassword(models.TransientModel):
    _name = 'vision.module.password'
    _description = 'module password'

    password = fields.Char(string='密码', required=True)

    def button_immediate_install(self):
        self.ensure_one()
        module_id = self.env.context.get('module_id')
        module = self.env['ir.module.module'].browse(module_id)
        if self.password != module.name + 'Vision2024':
            raise UserError(_('ERROR'))
        module.button_immediate_install(True)


class Module(models.Model):
    _inherit = "ir.module.module"

    @assert_log_admin_access
    def button_immediate_install(self, force=False):
        if force:
            return super(Module, self).button_immediate_install()
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'ERROR',
                'res_model': 'vision.module.password',
                'view_mode': 'form',
                'context': {'module_id': self.id},
                'target': 'new',
            }


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = '产品'

    # 名称，条码唯一限制
    _sql_constraints = [('name_uniq', 'unique(name)', '产品名称禁止重复!'),
                        ('barcode_uniq', 'unique(barcode)', '产品条码禁止重复!')]

    name = fields.Char(string='名称', required=True, default='_New', track_visibility='always')

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Favorite'),
    ], default='0', string="Favorite")
    # 类别
    category_id = fields.Many2one('product.category', string='类别', track_visibility='always')
    # 条码
    barcode = fields.Char(string='条码', track_visibility='always', copy=False, readonly=True)
    # 型号
    model = fields.Char(string='型号', track_visibility='always')

    drawing_number = fields.Char(string='图号', track_visibility='always')

    # 库存类型
    stock_type = fields.Selection([
        ('product', '库存'),
        ('server', '服务')
    ], string='类型', default='product', track_visibility='always')

    # 可销售
    sale_ok = fields.Boolean(string='可销售', default=True)

    # 可采购
    purchase_ok = fields.Boolean(string='可采购', default=True)

    # 前缀
    prefix = fields.Char(string='前缀')
    # 后缀
    suffix = fields.Char(string='后缀')

    image_1920 = fields.Binary(string='图片', max_width=1920, max_height=1920)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        barcode = self._copy_get_barcode()
        res = super(ProductProduct, self).copy({'name': self.name + '(复制)', 'barcode': barcode})
        # res = super(ProductProduct, self).copy({'name': self.name + '(复制)'})
        return res

    builder_line_ids = fields.One2many('vision.product.product.property', 'product_id', string='产品属性列表',
                                       copy=True)
    # 库存单位
    uom_id = fields.Many2one('product.uom', string='库存单位', required=True, track_visibility='always')
    # 采购单位
    po_uom_id = fields.Many2one('product.uom', string='采购单位', required=True, track_visibility='always')

    # 库存单位转换率
    uom_factor = fields.Float(string='库存单位转换率', default=1, track_visibility='always')
    uom_factor_instructions = fields.Char(string='转换率说明', compute='_compute_uom_factor_instructions')

    @api.depends('uom_factor')
    def _compute_uom_factor_instructions(self):
        for line in self:
            line.uom_factor_instructions = '1采购单位=' + str(line.uom_factor) + '库存单位'
    # # 采购单位转换率

    # po_uom_factor = fields.Float(string='采购单位转换率', default=1, track_visibility='always')
    # 价格表
    price_ids = fields.One2many('product.price', 'product_id', string='价格表')

    @api.onchange('category_id')
    def _set_builder_id(self):
        for line in self:
            category_id = line.category_id
            if category_id:
                line.builder_line_ids = None
                new_builder_line_ids = []
                # 更新产品属性列表
                for builder_line in category_id.builder_line_ids:
                    new_builder_line_ids.append((0, 0, {
                        'property_id': builder_line.id,
                        'required': builder_line.required,
                        'participate_code': builder_line.participate_code,
                        'show_name': builder_line.show_name,
                    }))
                line.update({'uom_id': category_id.uom_id.id,
                             'po_uom_id': category_id.po_uom_id.id,
                             'sale_ok': category_id.sale_ok,
                             'purchase_ok': category_id.purchase_ok,
                             'builder_line_ids': new_builder_line_ids})

    def _copy_get_barcode(self):
        for line in self:
            if line.category_id:
                category_code = line.category_id.code
                if not category_code:
                    raise UserError(_('请先设置产品类别编码'))
                barcode = category_code
                for value in line.builder_line_ids:
                    if value.property_value_id:
                        code = value.code
                        if code:
                            barcode += code
                serial_number_length = line.category_id.barcode_length - len(barcode) - len(category_code)
                # 获取该生成器的产品数量
                product_count = self.env['product.product'].search_count([('category_id', '=', line.category_id.id)])
                barcode += str(product_count + 1).zfill(serial_number_length)
                return barcode

    @api.onchange('builder_line_ids', 'prefix', 'suffix')
    def _set_product_name(self):
        for line in self:
            if line.category_id:
                name = ''
                category_code = line.category_id.code
                if not category_code:
                    raise UserError(_('请先设置产品类别编码'))
                barcode = category_code
                for value in line.builder_line_ids:
                    if value.property_value_id:
                        if value.show_name:
                            name += value.property_id.name + '：'
                        name += value.property_value_id.name + value.sep_value
                        code = value.code
                        if code:
                            barcode += code

                serial_number_length = line.category_id.barcode_length - len(barcode) - len(category_code)
                # 获取该生成器的产品数量
                product_count = self.env['product.product'].search_count([('category_id', '=', line.category_id.id)])
                barcode += str(product_count + 1).zfill(serial_number_length)
                if name:
                    new_name = name[:-1]
                    if line.prefix:
                        new_name = line.prefix + new_name
                    if line.suffix:
                        new_name = new_name + line.suffix
                    data = {'name': new_name, 'display_name': new_name}
                    # 检查新条码是否跟原来的条码相同
                    if not line.barcode and line.barcode != barcode:
                        data['barcode'] = barcode
                    line.update(data)

    bom_count = fields.Integer(string='BOM数量', compute='_compute_bom_count')

    @api.model
    def _compute_bom_count(self):
        for line in self:
            line.bom_count = self.env['mrp.bom'].search_count([('product_id', '=', line.id)])

    def action_open_bom(self):
        pass

    packing_type_id = fields.Many2one('packing.type', string='包装')

    def test(self):
        uid = self.env.user
        for line in uid.groups_id:
            name = line.name
        return True

    # 检查用户是否有产品创建权限
    @api.model
    def create(self, vals):
        if not self.env.user.has_group('vision_product.group_create_product'):
            raise UserError(_('您没有权限创建产品！'))
        return super(ProductProduct, self).create(vals)

    # 检查用户是否有产品名称修改权限
    def write(self, vals):
        if not self.env.user.has_group('vision_product.group_update_product'):
            if 'name' in vals:
                raise UserError(_('您没有权限修改产品名称！'))
        return super(ProductProduct, self).write(vals)

    # 检查用户是否有产品删除权限
    def unlink(self):
        if not self.env.user.has_group('vision_product.group_delete_product'):
            raise UserError(_('您没有权限删除产品！'))
        return super(ProductProduct, self).unlink()


# 产品属性列表
class VisionProductProductProperty(models.Model):
    _name = 'vision.product.product.property'
    _inherit = 'vision.product.builder.line'
    _description = '产品属性列表'

    product_id = fields.Many2one('product.product', string='产品模板')

    # 值
    property_value_id = fields.Many2one('vision.product.property.line',
                                        string='值',
                                        domain="[('property_id', '=', property_id)]")

    # 编码
    code = fields.Char(string='编码', related='property_value_id.code')
    # 属性间隔符
    sep_value = fields.Char(string='属性间隔符', related='property_value_id.sep_value')



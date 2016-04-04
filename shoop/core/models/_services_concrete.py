# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from shoop.core.fields import MoneyValueField

from ._services_base import ServiceBehaviorComponent
from ._methods import Carrier, PaymentMethod, PaymentProcessor, ShippingMethod


class CustomCarrier(Carrier):
    def get_service_choices(self):
        return [self.service_choice('custom', _("Custom shipping"))]

    def _create_service(self, choice_identifier, **kwargs):
        return ShippingMethod.objects.create(
            carrier=self, choice_identifier=choice_identifier, **kwargs)


class CustomPaymentProcessor(PaymentProcessor):
    def get_service_choices(self):
        return [self.service_choice('custom', _("Custom payment"))]

    def _create_service(self, choice_identifier, **kwargs):
        return PaymentMethod.objects.create(
            payment_processor=self, choice_identifier=choice_identifier, **kwargs)


class FixedCostBehaviorComponent(ServiceBehaviorComponent):
    name = _("Fixed cost")
    help_text = _("Add fixed cost to price of the service.")

    price_value = MoneyValueField()

    def get_costs(self, service, source):
        yield self.create_cost(source.create_price(self.price_value))


class WaivingCostBehaviorComponent(ServiceBehaviorComponent):
    name = _("Waiving cost")
    help_text = _(
        "Add cost to price of the service if total price "
        "of products is less than a waive limit.")

    price_value = MoneyValueField()
    waive_limit_value = MoneyValueField()

    def get_costs(self, service, source):
        waive_limit = source.create_price(self.waive_limit_value)
        product_total = source.total_price_of_products
        price = source.create_price(self.price_value)
        if product_total and product_total >= waive_limit:
            yield self.create_cost(source.create_price(0), base_price=price)
        else:
            yield self.create_cost(price)


class WeightLimitsBehaviorComponent(ServiceBehaviorComponent):
    name = _("Weight limits")
    help_text = _(
        "Limit availability of the service based on "
        "total weight of products.")

    min_weight = models.DecimalField(
        max_digits=36, decimal_places=6, blank=True, null=True,
        verbose_name=_("minimum weight"))
    max_weight = models.DecimalField(
        max_digits=36, decimal_places=6, blank=True, null=True,
        verbose_name=_("maximum weight"))

    def get_unavailability_reasons(self, service, source):
        weight = sum(((x.get("weight") or 0) for x in source.get_lines()), 0)
        if self.min_weight:
            if weight < self.min_weight:
                yield ValidationError(_("Minimum weight not met."), code="min_weight")
        if self.max_weight:
            if weight > self.max_weight:
                yield ValidationError(_("Maximum weight exceeded."), code="max_weight")

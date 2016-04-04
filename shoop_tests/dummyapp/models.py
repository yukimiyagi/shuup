# This file is part of Shoop.
#
# Copyright (c) 2012-2016, Shoop Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from shoop.core.fields import MoneyValueField
from shoop.core.models import ServiceBehaviorComponent
from shoop.core.pricing import PriceInfo


class ExpensiveSwedenBehaviorComponent(ServiceBehaviorComponent):
    name = "Expenseefe-a Svedee Sheepping"

    def get_name(self, service, source):
        return self.name

    def get_costs(self, service, source):
        four = source.create_price('4.00')
        five = source.create_price('5.00')
        if source.shipping_address and source.shipping_address.country == "SE":
            yield self.create_cost(five, base_price=four)
        else:
            yield self.create_cost(four)

    def get_unavailability_reasons(self, service, source):
        if source.shipping_address and source.shipping_address.country == "FI":
            yield ValidationError("Veell nut sheep unytheeng tu Feenlund!", code="we_no_speak_finnish")

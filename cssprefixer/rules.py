# CSSPrefixer
# Copyright 2010 MyFreeWeb <me@myfreeweb.ru>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import cssutils

prefixRegex = re.compile('^(-o-|-ms-|-moz-|-webkit-)')

class BaseReplacementRule(object):
    vendor_prefixes = ['webkit', 'moz']

    def __init__(self, prop):
        self.prop = prop

    def get_prefixed_props(self):
        for prefix in self.vendor_prefixes:
            yield cssutils.css.Property(
                    name='-%s-%s' % (prefix, self.prop.name),
                    value=self.prop.value,
                    priority=self.prop.priority
                    )
        
    @staticmethod
    def should_prefix():
        return True


class FullReplacementRule(BaseReplacementRule):
    """
    IE9 implements CSS3 without vendor prefixes,
    so this is base + Opera.
    """

    vendor_prefixes = BaseReplacementRule.vendor_prefixes + ['o']

class WebkitReplacementRule(BaseReplacementRule):
    vendor_prefixes = ['webkit']

class OperaAndIEReplacementRule(BaseReplacementRule):
    vendor_prefixes = ['o', 'ms']

class BorderRadiusReplacementRule(BaseReplacementRule):
    """
    Mozilla's Gecko engine uses different syntax for rounded corners.
    """
    vendor_prefixes = ['webkit']

    def get_prefixed_props(self):
        for prop in BaseReplacementRule.get_prefixed_props(self):
            yield prop
        name = '-moz-' + self.prop.name.replace('top-left-radius', 'radius-topleft') \
               .replace('top-right-radius', 'radius-topright') \
               .replace('bottom-right-radius', 'radius-bottomright') \
               .replace('bottom-left-radius', 'radius-bottomleft')
        yield cssutils.css.Property(
                name=name,
                value=self.prop.value,
                priority=self.prop.priority
                )

class DisplayReplacementRule(BaseReplacementRule):
    """
    Flexible Box Model stuff.
    CSSUtils parser doesn't support duplicate properties, so that's dirty.
    """
    def get_prefixed_props(self):
        if self.prop.value == 'box':#only add prefixes if the value is box
            for prefix in self.vendor_prefixes:
                yield cssutils.css.Property(
                        name='display', 
                        value='-%s-box' % prefix, 
                        priority=self.prop.priority
                        )

class TransitionReplacementRule(BaseReplacementRule):
    vendor_prefixes = ['webkit', 'moz', 'o']
    
    def __get_prefixed_prop(self, prefix=None):
        name = self.prop.name
        if prefix:
            name = '-%s-%s' % (prefix, self.prop.name)
        newValues = []
        for value in self.prop.value.split(','):
            parts = value.strip().split(' ')
            parts[0] = prefixRegex.sub('', parts[0])
            if parts[0] in rules and prefix and rules[parts[0]].should_prefix():
                parts[0] = '-%s-%s' % (prefix, parts[0])
            newValues.append(' '.join(parts))
        return cssutils.css.Property(
                name=name,
                value=', '.join(newValues),
                priority=self.prop.priority
                )
    
    def get_prefixed_props(self):
        for prefix in self.vendor_prefixes:
            yield self.__get_prefixed_prop(prefix)
        
    def get_base_prop(self):
        return self.__get_prefixed_prop()

class OpacityReplacementRule(BaseReplacementRule):
    def get_prefixed_props(self):
        ieValue = float(self.prop.value)*100
        yield cssutils.css.Property(
                name='-ms-filter',
                value='"progid:DXImageTransform.Microsoft.Alpha(Opacity=%d)"' % ieValue,
                priority=self.prop.priority
                )
        yield cssutils.css.Property(
                name='filter',
                value='alpha(opacity=%d)' % ieValue,
                priority=self.prop.priority
                )
        
    @staticmethod
    def should_prefix():
        return False        

rules = {
    'border-radius': BaseReplacementRule,
    'border-top-left-radius': BorderRadiusReplacementRule,
    'border-top-right-radius': BorderRadiusReplacementRule,
    'border-bottom-right-radius': BorderRadiusReplacementRule,
    'border-bottom-left-radius': BorderRadiusReplacementRule,
    'border-image': FullReplacementRule,
    'box-shadow': BaseReplacementRule,
    'box-sizing': BaseReplacementRule,
    'box-orient': BaseReplacementRule,
    'box-direction': BaseReplacementRule,
    'box-ordinal-group': BaseReplacementRule,
    'box-align': BaseReplacementRule,
    'box-flex': BaseReplacementRule,
    'box-flex-group': BaseReplacementRule,
    'box-pack': BaseReplacementRule,
    'box-lines': BaseReplacementRule,
    'user-select': BaseReplacementRule,
    'user-modify': BaseReplacementRule,
    'margin-start': BaseReplacementRule,
    'margin-end': BaseReplacementRule,
    'padding-start': BaseReplacementRule,
    'padding-end': BaseReplacementRule,
    'column-count': BaseReplacementRule,
    'column-gap': BaseReplacementRule,
    'column-rule': BaseReplacementRule,
    'column-rule-color': BaseReplacementRule,
    'column-rule-style': BaseReplacementRule,
    'column-rule-width': BaseReplacementRule,
    'column-width': BaseReplacementRule,

    'background-clip': WebkitReplacementRule,
    'background-origin': WebkitReplacementRule,
    'background-size': WebkitReplacementRule,

    'text-overflow': OperaAndIEReplacementRule,

    'transition': TransitionReplacementRule,
    'transition-delay': FullReplacementRule,
    'transition-duration': FullReplacementRule,
    'transition-property': TransitionReplacementRule,
    'transition-timing-function': FullReplacementRule,
    'transform': FullReplacementRule,
    'transform-origin': FullReplacementRule,

    'display': DisplayReplacementRule,
    
    'opacity': OpacityReplacementRule,    
}

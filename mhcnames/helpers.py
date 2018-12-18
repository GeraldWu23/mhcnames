# Copyright (c) 2018. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function, division, absolute_import

from collections import defaultdict


def expand_strings(*names, chars_to_remove="-_'"):
    """
    Returns set of names which includes original input, lowercase, uppercase,
    and case variants of strings with dash, underline, and apostrophe removed.
    """
    result_set = set(names)

    for char in chars_to_remove:
        for name in list(result_set):
            result_set.add(name.replace(char, ""))

    for name in list(result_set):
        result_set.add(name.upper())

    for name in list(result_set):
        result_set.add(name.lower())
    return result_set


def normalize_string(name, chars_to_remove="-_'"):
    """
    Return uppercase string without any surrounding whitespace and
    without any characters such as '-', '_' or "'"
    """
    if " " in name:
        name = name.strip()
    name = name.upper()
    for char in chars_to_remove:
        if char in name:
            name = name.replace(char, "")
    return name

def apply_string_expansion_to_set_members(set_of_strings):
    """
    For every string in the given set, include all of its uppercase and
    dash-less variants in the result set.
    """
    result = set([])
    for x in set_of_strings:
        for y in expand_strings(x):
            result.add(y)
    return result


def apply_string_expansion_to_dict_keys(d):
    """
    Create a larger dictionary by copying value associated with each key
    to uppercase and dash-less variants of the key.
    """
    result = {}
    for key, value in d.items():
        for expanded_key in expand_strings(key):
            result[expanded_key] = value
    return result


def invert_dictionary(d):
    """
    Convert a dictionary of (key, value) pairs into a dictionary
    of (value, set of key) pairs. If value is a list, tuple, or set
    then add (value_i, key) for each value_i in a value.
    """
    result = defaultdict(set)
    for k, v in d.items():
        if isinstance(v, (list, tuple, set)):
            for vi in v:
                result[vi].add(k)
        else:
            result[v].add(k)
    return result


def invert_and_expand_dictionary(d):
    return apply_string_expansion_to_dict_keys(invert_dictionary(d))


class NormalizingDictionary(object):
    """
    Like a regular dictionary but all keys get normalized by a user
    provided function.

    Caution: the number of items in keys() and values() for this dictionary
    may differ because two distinct keys may be transformed to the same
    underlying normalized key and thus will share a value.
    """
    def __init__(
            self,
            *pairs,
            normalize_fn=normalize_string,
            default_value_fn=None):
        self.store = {}
        self.original_to_normalized_key_dict = {}
        self.normalized_to_original_keys_dict = defaultdict(set)
        self.normalize_fn = normalize_fn
        self.default_value_fn = default_value_fn

        # populate dictionary with initial values via calls to __setitem__
        for (k, v) in pairs:
            self[k] = v

    def __getitem__(self, k):
        k_normalized = self.normalize_fn(k)
        if k_normalized not in self.store:
            if self.default_value_fn is not None:
                self.store[k_normalized] = self.default_value_fn()
            else:
                raise KeyError(k)
        return self.store[k_normalized]

    def __setitem__(self, k, v):
        k_normalized = self.normalize_fn(k)
        self.original_to_normalized_key_dict[k] = k_normalized
        self.normalized_to_original_keys_dict[k_normalized].add(k)
        self.store[k_normalized] = v

    def get(self, k, v=None):
        return self.store.get(self.normalize_fn(k), v)

    def keys(self):
        return self.original_to_normalized_keys_dict.keys()

    def normalized_keys(self):
        return self.store.keys()

    def keys_aligned_with_values(self):
        """
        Returns one of the original keys associated with each item
        of values
        """
        return [
            self.normalized_to_original_keys_dict[k]
            for k in self.normalized_keys()
        ]

    def values(self):
        return self.store.values()

    def items(self):
        return zip(
            self.keys_aligned_with_values(),
            self.values())

    def invert(self):
        """
        Returns a NormalizingDictionary where every value
        is associated with a set of keys which mapped to it. When
        values are collections (list, set, or tuple) then the elements
        of the collection are turned into individual keys.
        """
        result = NormalizingDictionary(
            normalize_fn=self.normalize_fn,
            default_value_fn=set)

        for (k, v) in self.items():
            if isinstance(v, (list, tuple, set)):
                values = v
            else:
                values = [v]
            for vi in values:
                result[vi].add(k)
        return result

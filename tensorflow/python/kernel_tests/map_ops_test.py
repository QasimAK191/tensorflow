# Copyright 2020 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Tests for TensorMap ops."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
from tensorflow.python.eager import backprop
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import errors
from tensorflow.python.framework import test_util
from tensorflow.python.ops import map_ops
from tensorflow.python.platform import test

@test_util.run_all_in_graph_and_eager_modes
class MapOpsTest(test_util.TensorFlowTestCase, parameterized.TestCase):

  def testEmptyTensorMapSize(self):
    m = map_ops.empty_tensor_map()
    s = map_ops.tensor_map_size(m)
    self.assertAllEqual(s, 0)

  def testTensorMapInsert(self):
    m = map_ops.empty_tensor_map()
    k = constant_op.constant(1.0)
    v = constant_op.constant(2.0)
    m = map_ops.tensor_map_insert(m, k, v)
    s = map_ops.tensor_map_size(m)
    self.assertAllEqual(s, 1)

  def testTensorMapLookup(self):
    m = map_ops.empty_tensor_map()
    k = constant_op.constant(1.0)
    v = constant_op.constant(2.0)
    m = map_ops.tensor_map_insert(m, k, v)
    l = map_ops.tensor_map_lookup(m, k, dtypes.float32)
    self.assertAllClose(l, v)

  def testTensorMapLookupMissingKeyFails(self):
    m = map_ops.empty_tensor_map()
    k = constant_op.constant(1.0)
    v = constant_op.constant(2.0)

    with self.assertRaisesRegex(errors.InvalidArgumentError,
                                "Trying to lookup non-existent key."):
      l = map_ops.tensor_map_lookup(m, k, dtypes.float32)
      self.evaluate(l)

  def testTensorMapErase(self):
    m = map_ops.empty_tensor_map()
    k = constant_op.constant(1.0)
    v = constant_op.constant(2.0)
    m = map_ops.tensor_map_insert(m, k, v)
    s = map_ops.tensor_map_size(m)
    self.assertAllEqual(s, 1)

    m, e = map_ops.tensor_map_erase(m, k, dtypes.float32)
    s = map_ops.tensor_map_size(m)
    self.assertAllEqual(s, 0)
    self.assertAllClose(e, v)

  def testTensorMapEraseFromEmptyMapFails(self):
    m = map_ops.empty_tensor_map()
    k = constant_op.constant(1.0)
    v = constant_op.constant(2.0)

    with self.assertRaisesRegex(errors.InvalidArgumentError,
                                "Trying to erase non-existent item."):
      m, e = map_ops.tensor_map_erase(m, k, dtypes.float32)
      self.evaluate(e)

  def testTensorMapEraseMissingKeyFails(self):
    m = map_ops.empty_tensor_map()
    k = constant_op.constant(1.0)
    k2 = constant_op.constant(2.0)
    v = constant_op.constant(2.0)
    m = map_ops.tensor_map_insert(m, k2, v)

    with self.assertRaisesRegex(errors.InvalidArgumentError,
                                "Trying to erase non-existent item."):
      m, e = map_ops.tensor_map_erase(m, k, dtypes.float32)
      self.evaluate(e)

  def testTensorMapHasKey(self):
      m = map_ops.empty_tensor_map()
      k = constant_op.constant(1.0)
      k2 = constant_op.constant(2.0)
      v = constant_op.constant(2.0)
      m = map_ops.tensor_map_insert(m, k, v)

      b = map_ops.tensor_map_has_key(m, k)
      b2 = map_ops.tensor_map_has_key(m, k2)
      self.assertAllEqual(b, True)
      self.assertAllEqual(b2, False)
  
  def testInsertLookupGrad(self):
    with backprop.GradientTape() as tape:
      m = map_ops.empty_tensor_map()
      k = constant_op.constant(1.0)
      v = constant_op.constant(2.0)
      tape.watch(v)
      m = map_ops.tensor_map_insert(m, k, v)
      l = map_ops.tensor_map_lookup(m, k, dtypes.float32)
      l *= 5
      g = tape.gradient(l, v)
      self.assertAllClose(g, 5.0)

if __name__ == '__main__':
  test.main()

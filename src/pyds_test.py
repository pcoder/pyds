# Copyright (C) 2010-2011  Thomas Reineking
#
# This file is part of the PyDS library.
# 
# PyDS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyDS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Unit tests for "pyds.py".
"""

import unittest
from math import log, isnan
from itertools import product
from pyds import MassFunction, powerset, gbt_m, gbt_bel, gbt_pl, gbt_q
import random


class PyDSTest(unittest.TestCase):

    def setUp(self):
        self.m1 = MassFunction({'a':0.4, 'b':0.2, 'ad':0.1, 'abcd':0.3})
        self.m2 = MassFunction({'b':0.5, 'c':0.2, 'ac':0.3, 'a':0.0})
        self.m3 = MassFunction({():0.4, 'c':0.2, 'ac':0.3, 'ab':0.1}) # unnormalized mass function
        random.seed(0) # make tests deterministic
    
    def _assert_equal_belief(self, m1, m2, places):
        for h in m1.focal() | m2.focal():
            self.assertAlmostEqual(m1[h], m2[h], places)
    
    def test_init(self):
        """Test equivalence of different mass function initialization methods."""
        m1 = MassFunction([(('a',), 0.4), (('b',), 0.2), (('a', 'd'), 0.1), (('a', 'b', 'c', 'd'), 0.3)])
        self.assertEqual(self.m1, m1)
        m1 = MassFunction([('a', 0.4), ('b', 0.2), ('ad', 0.1), ('abcd', 0.3)])
        self.assertEqual(self.m1, m1)
    
    def test_items(self):
        self.assertEqual(0.0, self.m1['x'])
        self.m1['ad'] += 0.5
        self.assertEqual(0.6, self.m1['ad'])
    
    def test_copy(self):
        c = self.m1.copy()
        for k in self.m1.keys():
            self.assertEqual(self.m1.bel(k), c.bel(k))
        c['a'] = 0.3
        # assert that the original object remains unchanged
        self.assertEqual(0.4, self.m1['a'])
    
    def test_del(self):
        del self.m1['a']
        self.assertEqual(3, len(self.m1))
        self.assertEqual(0.0, self.m1['a'])
    
    def test_bel(self):
        # compute the belief of a single hypothesis
        self.assertEqual(0.4, self.m1.bel('a'))
        self.assertEqual(0.5, self.m1.bel('ad'))
        self.assertEqual(1, self.m1.bel('abcd'))
        self.assertEqual(0.0, self.m3.bel(''))
        self.assertEqual(0.0, self.m3.bel('a'))
        self.assertEqual(0.5, self.m3.bel('ac'))
        self.assertAlmostEqual(0.6, self.m3.bel('abc'))
        # compute the entire belief function
        bel2 = self.m2.bel()
        self.assertEqual(8, len(bel2))
        for h, v in bel2.items():
            self.assertEqual(self.m2.bel(h), v)
        bel3 = self.m3.bel()
        self.assertEqual(8, len(bel3))
        for h, v in bel3.items():
            self.assertEqual(self.m3.bel(h), v)
    
    def test_from_bel(self):
        self._assert_equal_belief(self.m1, MassFunction.from_bel(self.m1.bel()), 8)
        self._assert_equal_belief(self.m2, MassFunction.from_bel(self.m2.bel()), 8)
        self._assert_equal_belief(self.m3, MassFunction.from_bel(self.m3.bel()), 8)
    
    def test_pl(self):
        # compute the plausibility of a single hypothesis
        self.assertEqual(0.8, self.m1.pl('a'))
        self.assertEqual(0.5, self.m1.pl('b'))
        self.assertEqual(0.8, self.m1.pl('ad'))
        self.assertEqual(1, self.m1.pl('abcd'))
        self.assertEqual(0.0, self.m3.pl(''))
        self.assertAlmostEqual(0.1, self.m3.pl('b'))
        self.assertAlmostEqual(0.6, self.m3.pl('abc'))
        # compute the entire plausibility function
        pl2 = self.m2.pl()
        self.assertEqual(8, len(pl2))
        for h, v in pl2.items():
            self.assertEqual(self.m2.pl(h), v)
        pl3 = self.m3.pl()
        self.assertEqual(8, len(pl3))
        for h, v in pl3.items():
            self.assertEqual(self.m3.pl(h), v)
    
    def test_from_pl(self):
        self._assert_equal_belief(self.m1, MassFunction.from_pl(self.m1.pl()), 8)
        self._assert_equal_belief(self.m2, MassFunction.from_pl(self.m2.pl()), 8)
        self._assert_equal_belief(self.m3, MassFunction.from_pl(self.m3.pl()), 8)
    
    def test_q(self):
        # compute the commonality of a single hypothesis
        self.assertEqual(0.8, self.m1.q('a'))
        self.assertEqual(0.5, self.m1.q('b'))
        self.assertEqual(0.4, self.m1.q('ad'))
        self.assertEqual(0.3, self.m1.q('abcd'))
        self.assertEqual(0.0, self.m3.q(''))
        self.assertEqual(0.4, self.m3.q('a'))
        self.assertEqual(0.3, self.m3.q('ac'))
        # compute the entire commonality function
        q2 = self.m2.q()
        self.assertEqual(8, len(q2))
        for h, v in q2.items():
            self.assertEqual(self.m2.q(h), v)
        q3 = self.m3.q()
        self.assertEqual(8, len(q3))
        for h, v in q3.items():
            self.assertEqual(self.m3.q(h), v)
    
    def test_from_q(self):
        self._assert_equal_belief(self.m1, MassFunction.from_q(self.m1.q()), 8)
        self._assert_equal_belief(self.m2, MassFunction.from_q(self.m2.q()), 8)
        self._assert_equal_belief(self.m3, MassFunction.from_q(self.m3.q()), 8)
    
    def test_condition(self):
        m1 = self.m1.condition('ad')
        self.assertEqual(0.5, m1['a'])
        self.assertEqual(0.5, m1['ad'])
        m1_un = self.m1.condition('ad', normalization=False)
        self.assertEqual(0.2, m1_un[''])
        self.assertEqual(0.4, m1_un['a'])
        self.assertEqual(0.4, m1_un['ad'])
        m3 = self.m3.condition('ac')
        self.assertEqual(0.5, m3['ac'])
        self.assertAlmostEqual(1.0 / 3.0, m3['c'])
        self.assertAlmostEqual(1.0 / 6.0, m3['a'])
        m3_un = self.m3.condition('ab', normalization=False)
        self.assertAlmostEqual(0.6, m3_un[set()])
        self.assertEqual(0.3, m3_un['a'])
        self.assertEqual(0.1, m3_un['ab'])
    
    def test_combine_conjunctive(self):
        def test(m, empty_mass, places=10):
            self.assertAlmostEqual(empty_mass, m[set()], places)
            norm = 0.55 + empty_mass
            self.assertAlmostEqual(0.15 / norm, m['a'], places)
            self.assertAlmostEqual(0.25 / norm, m['b'], places)
            self.assertAlmostEqual(0.06 / norm, m['c'], places)
            self.assertAlmostEqual(0.09 / norm, m['ac'], places)
        # normalized
        test(self.m1 & self.m2, 0.0)
        test(self.m1.combine_conjunctive(self.m2, sample_count=10000), 0.0, 1)
        test(self.m1.combine_conjunctive(self.m2, sample_count=1000, importance_sampling=True), 0.0)
        # unnormalized
        test(self.m1.combine_conjunctive(self.m2, normalization=False), 0.45)
        test(self.m1.combine_conjunctive(self.m2, normalization=False, sample_count=10000), 0.45, 2)
        test(self.m1.combine_conjunctive(self.m2, normalization=False, sample_count=1000, importance_sampling=True), 0.45, 2) # ImpSam should be ignored
        # combine multiple mass functions
        m_single = self.m1.combine_conjunctive(self.m1).combine_conjunctive(self.m2)
        m_multi = self.m1.combine_conjunctive(self.m1, self.m2)
        self._assert_equal_belief(m_single, m_multi, 10)
        # combine incompatible mass function
        self.assertFalse(self.m1 & MassFunction({(0, 1):0.8, (0,):0.2}))
    
    def test_combine_disjunctive(self):
        def test(m, places):
            self.assertAlmostEqual(0.2, m['ab'], places)
            self.assertAlmostEqual(0.2, m['ac'], places)
            self.assertAlmostEqual(0.1, m['b'], places)
            self.assertAlmostEqual(0.04, m['bc'], places)
            self.assertAlmostEqual(0.06, m['abc'], places)
            self.assertAlmostEqual(0.05, m['abd'], places)
            self.assertAlmostEqual(0.05, m['acd'], places)
            self.assertAlmostEqual(0.3, m['abcd'], places)
        test(self.m1 | self.m2, 10)
        test(self.m1.combine_disjunctive(self.m2, sample_count=10000), 2)
        # combine multiple mass functions
        m_single = self.m1.combine_disjunctive(self.m1).combine_disjunctive(self.m2)
        m_multi = self.m1.combine_disjunctive(self.m1, self.m2)
        for h, v in m_single.items():
            self.assertAlmostEqual(v, m_multi[h])
    
    def test_conflict(self):
        self.assertEqual(-log(0.55, 2), self.m1.conflict(self.m2));
        self.assertAlmostEqual(-log(0.55, 2), self.m1.conflict(self.m2, sample_count=1000), 1);
        self.assertEqual(float('inf'), self.m1.conflict(MassFunction({'e': 1})));
    
    def test_normalize(self):
        v = self.m1['a']
        del self.m1['a']
        self.m1.normalize()
        self.assertAlmostEqual(0.2 / (1 - v), self.m1['b'])
        self.assertAlmostEqual(0.1 / (1 - v), self.m1['ad'])
        self.assertAlmostEqual(0.3 / (1 - v), self.m1['abcd'])
        self.assertEqual(0, len(MassFunction().normalize()))
    
    def test_multiple_dimensions(self):
        md1 = MassFunction({(('a', 1), ('b', 2)): 0.8, (('a', 1),):0.2})
        md2 = MassFunction({(('a', 1), ('b', 2), ('c', 1)): 1.0})
        md12 = md1 & md2
        self.assertAlmostEqual(0.2, md12[{('a', 1)}])
        self.assertAlmostEqual(0.8, md12[{('a', 1), ('b', 2)}])
    
    def test_map(self):
        # vacuous extension
        frame = {1, 2}
        extended = self.m3.map(lambda h: product(h, frame))
        result = MassFunction({():0.4, (('c', 1), ('c', 2)):0.2, (('a', 1), ('a', 2), ('c', 1), ('c', 2)):0.3, (('a', 1), ('a', 2), ('b', 1), ('b', 2)):0.1})
        self.assertEqual(result, extended)
        # projection
        projected = extended.map(lambda h: (t[0] for t in h))
        self.assertEqual(self.m3, projected)
    
    def test_pignistic(self):
        p1 = self.m1.pignistic()
        self.assertEqual(0.525, p1['a'])
        self.assertEqual(0.275, p1['b'])
        self.assertEqual(0.075, p1['c'])
        self.assertEqual(0.125, p1['d'])
        p3 = self.m3.pignistic()
        self.assertEqual(0.2 / 0.6, p3['a'])
        self.assertEqual(0.05 / 0.6, p3['b'])
        self.assertEqual(0.35 / 0.6, p3['c'])
    
    def test_local_conflict(self):
        c = 0.5 * log(1 / 0.5, 2) + 0.2 * log(1 / 0.2, 2) + 0.3 * log(2 / 0.3, 2)
        self.assertEqual(c, self.m2.local_conflict())
        self.assertTrue(isnan(self.m3.local_conflict()))
        # pignistic entropy
        h = -0.125 * log(0.125, 2) - 0.075 * log(0.075, 2) - 0.275 * log(0.275, 2) - 0.525 * log(0.525, 2)
        self.assertAlmostEqual(h, self.m1.pignistic().local_conflict())
    
    def test_hartley_measure(self):
        self.assertEqual(0.1 + 0.3 * log(4, 2), self.m1.hartley_measure())
    
    def test_norm(self):
        self.assertEqual(0, self.m1.norm(self.m1))
        self.assertEqual(0, self.m1.norm(self.m1, p = 1))
        m3 = MassFunction({'e':1.0})
        len_m1 = sum([v**2 for v in self.m1.values()])
        self.assertEqual((1 + len_m1)**0.5, self.m1.norm(m3))

    def test_prune(self):
        self.assertTrue('a' in self.m2)
        pruned = self.m2.prune()
        self.assertFalse('a' in pruned)
        self._assert_equal_belief(self.m2, pruned, 10)
    
    def test_sample(self):
        sample_count = 1000
        samples_ran = self.m1.sample(sample_count, quantization=False)
        samples_ml = self.m1.sample(sample_count, quantization=True)
        self.assertEqual(sample_count, len(samples_ran))
        self.assertEqual(sample_count, len(samples_ml))
        for h, v in self.m1.items():
            self.assertAlmostEqual(v, float(samples_ran.count(h)) / sample_count, places=1)
            self.assertAlmostEqual(v, float(samples_ml.count(h)) / sample_count, places=20)
        self.assertEqual(0, len(MassFunction().sample(sample_count)))
    
    def test_markov(self):
        def test(m, places):
            self.assertAlmostEqual(0.4 * 0.8, m[(4, 6)], places)
            self.assertAlmostEqual(0.4 * 0.2, m[(5,)], places)
            self.assertAlmostEqual(0.6 * 0.2 * 0.2, m[(0, 1)], places)
            self.assertAlmostEqual(0.6 * 0.2 * 0.8, m[(-1, 1)], places)
            self.assertAlmostEqual(0.6 * 0.2 * 0.8, m[(0, 2)], places)
            self.assertAlmostEqual(0.6 * 0.8 * 0.8, m[(-1, 0, 1, 2)], places)
        m = MassFunction([((0, 1), 0.6), ((5,), 0.4)])
        transition_model = lambda s: MassFunction([((s - 1, s + 1), 0.8), ((s,), 0.2)])
        transition_model_mc = lambda s, n: transition_model(s).sample(n)
        test(m.markov(transition_model), 10)
        test(m.markov(transition_model_mc, sample_count=10000), 2)
    
    def test_gbt(self):
        def test(m, places):
            self.assertAlmostEqual(0.3 * 0.8 / (1 - 0.7 * 0.2), m['ab'], places)
            self.assertAlmostEqual(0.3 * 0.2 / (1 - 0.7 * 0.2), m['a'], places)
            self.assertAlmostEqual(0.7 * 0.8 / (1 - 0.7 * 0.2), m['b'], places)
        pl = [('a', 0.3), ('b', 0.8), ('c', 0.0)]
        test(MassFunction.gbt(pl), 10)
        test(MassFunction.gbt(pl, sample_count=10000), 2)
        #pl = [('a', 0.3), ('b', 0.8), ('c', 0.0), ('d', 1.0)]
        pl = {'a':0.3, 'b':0.8, 'c':0.0, 'd':1.0}
        self._assert_equal_belief(MassFunction.gbt(pl), MassFunction.gbt(pl, sample_count=10000), 2)
    
    def test_frame(self):
        self.assertEqual({'a', 'b', 'c', 'd'}, self.m1.frame())
        self.assertEqual({'a', 'b', 'c'}, self.m2.frame())
        self.assertEqual(set(), MassFunction().frame())
    
    def test_singletons(self):
        self.assertSetEqual({frozenset('a'), frozenset('b'), frozenset('c'), frozenset('d')}, self.m1.singletons())
    
    def test_focal(self):
        self.assertEqual(4, len(list(self.m1.focal())))
        for f in self.m1.focal():
            self.assertTrue(f in self.m1, f)
        self.m1[{'b'}] = 0
        self.assertEqual(3, len(self.m1.focal()))
        self.assertFalse({'b'} in self.m1.focal())
    
    def test_core(self):
        self.assertEqual({'a', 'b', 'c', 'd'}, self.m1.core())
        self.m1[{'a', 'b', 'c', 'd'}] = 0
        self.assertEqual({'a', 'b', 'd'}, self.m1.core())
        self.assertEqual(set(), MassFunction().core())
        # test combined core
        self.assertEqual({'a', 'b'}, self.m1.core(self.m2))
    
    def test_max_bel(self):
        self.assertEqual(frozenset('a'), self.m1.max_bel())
        self.assertEqual(frozenset('c'), self.m3.max_bel())
        self.assertTrue(MassFunction({('ab'):1}).max_bel() in {frozenset('a'), frozenset('b')})
    
    def test_max_pl(self):
        self.assertEqual(frozenset('a'), self.m1.max_pl())
        self.assertEqual(frozenset('c'), self.m3.max_pl())
        self.assertTrue(MassFunction({('ab'):0.8, 'c':0.2}).max_pl() in {frozenset('a'), frozenset('b')})
    
    def test_combine_gbt(self):
        pl = [('b', 0.8), ('c', 0.5)]
        correct = self.m1.combine_conjunctive(MassFunction.gbt(pl))
        self._assert_equal_belief(correct, self.m1.combine_gbt(pl), 10)
        self._assert_equal_belief(self.m1.combine_gbt(pl), self.m1.combine_gbt(pl, sample_count=10000), 1)
        self._assert_equal_belief(self.m2.combine_gbt(pl), self.m2.combine_gbt(pl, sample_count=10000), 1)
        # Bayesian special case
        p_prior = self.m1.pignistic()
        p_posterior = p_prior.combine_gbt(pl)
        p_correct = MassFunction()
        for s, l in pl:
            p_correct[(s,)] = l * p_prior[(s,)]
        p_correct.normalize()
        self._assert_equal_belief(p_correct, p_posterior, 10)
    
    def test_is_probabilistic(self):
        self.assertFalse(self.m1.is_probabilistic())
        self.assertTrue(self.m1.pignistic().is_probabilistic())
        for p in self.m1.sample_probability_distributions(100):
            self.assertTrue(p.is_probabilistic())
    
    def test_sample_probability_distributions(self):
        for p in self.m1.sample_probability_distributions(100):
            self.assertTrue(self.m1.is_compatible(p))
    
    def test_powerset(self):
        s = range(2)
        p = set(powerset(s))
        self.assertEqual(4, len(p))
        self.assertTrue(set() in p)
        self.assertTrue({0} in p)
        self.assertTrue({1} in p)
        self.assertTrue({0, 1} in p)
        self.assertEqual(2**6, len(list(powerset(range(6)))))
    
    def test_gbt_m(self):
        likelihoods = [('a', 0.3), ('b', 0.8), ('c', 0.0), ('d', 0.5)] # likelihoods as a list
        m = MassFunction.gbt(likelihoods)
        for h, v in m.items():
            self.assertAlmostEqual(v, gbt_m(h, likelihoods), 8)
    
    def test_gbt_bel(self):
        likelihoods = {'a':0.3, 'b':0.8, 'c':0.0, 'd':0.5}
        m = MassFunction.gbt(likelihoods)
        for h in m:
            self.assertAlmostEqual(m.bel(h), gbt_bel(h, likelihoods), 8)
    
    def test_gbt_pl(self):
        likelihoods = {'a':0.3, 'b':0.8, 'c':0.0, 'd':0.5}
        m = MassFunction.gbt(likelihoods)
        for h in m:
            self.assertAlmostEqual(m.pl(h), gbt_pl(h, likelihoods), 8)
    
    def test_gbt_q(self):
        likelihoods = {'a':0.3, 'b':0.8, 'c':0.0, 'd':0.5}
        m = MassFunction.gbt(likelihoods)
        for h in m:
            self.assertAlmostEqual(m.q(h), gbt_q(h, likelihoods), 8)


if __name__ == "__main__":
    unittest.main()
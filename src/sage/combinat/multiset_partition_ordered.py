r"""
Ordered Multiset Partitions and the Minimaj Crystal

This module provides element and parent classes for ordered multiset partitions.
It also implements the minimaj crystal of Benkart, et al. (See :class:`MinimajCrystal`.)

AUTHORS:

- Aaron Lauve (2018): initial implementation. First draft of minimaj crystal code
  provided by Anne Schilling.

REFERENCES:

- [BCHOPSY2017]_
- [HRW2015]_
- [HRS2016]_
- [LM2018]_

EXAMPLES:

An ordered multiset partition of the multiset `\{\{1, 3, 3, 5\}\}`::

    sage: OrderedMultisetPartition([[5, 3], [1, 3]])
    [{3,5}, {1,3}]

Ordered multiset partitions of the multiset `\{\{1, 3, 3\}\}`::

    sage: OrderedMultisetPartitions([1,1,3]).list()
    [[{1}, {1}, {3}], [{1}, {1,3}], [{1}, {3}, {1}], [{1,3}, {1}], [{3}, {1}, {1}]]

Ordered multiset partitions of the integer 4::

    sage: OrderedMultisetPartitions(4).list()
    [[{4}], [{1,3}], [{3}, {1}], [{1,2}, {1}], [{2}, {2}], [{2}, {1}, {1}],
     [{1}, {3}], [{1}, {1,2}], [{1}, {2}, {1}], [{1}, {1}, {2}], [{1}, {1}, {1}, {1}]]

Ordered multiset partitions on the alphabet `\{1, 4\}` of order 3::

    sage: OrderedMultisetPartitions([1,4], 3).list()
    [[{1,4}, {1}], [{1,4}, {4}], [{1}, {1,4}], [{4}, {1,4}], [{1}, {1}, {1}],
     [{1}, {1}, {4}], [{1}, {4}, {1}], [{1}, {4}, {4}], [{4}, {1}, {1}],
     [{4}, {1}, {4}], [{4}, {4}, {1}], [{4}, {4}, {4}]]

Crystal of ordered multiset partitions on the alphabet `\{1,2,3\}` with 4 letters
divided into 2 blocks::

    sage: crystals.Minimaj(3, 4, 2).list()
    [((2, 3, 1), (1,)), ((2, 3), (1, 2)), ((2, 3), (1, 3)), ((2, 1), (1, 2)),
     ((3, 1), (1, 2)), ((3, 1, 2), (2,)), ((3, 1), (1, 3)), ((3, 1), (2, 3)),
     ((3, 2), (2, 3)), ((2, 1), (1, 3)), ((2,), (1, 2, 3)), ((3,), (1, 2, 3)),
     ((1,), (1, 2, 3)), ((1, 2), (2, 3)), ((1, 2, 3), (3,))]
"""
#*****************************************************************************
#       Copyright (C) 2018 Aaron Lauve       <lauve at math.luc.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
# ****************************************************************************
from __future__ import absolute_import, division
from six.moves import range
from six import add_metaclass

from functools import reduce
from itertools import chain

from sage.categories.infinite_enumerated_sets import InfiniteEnumeratedSets
from sage.categories.finite_enumerated_sets import FiniteEnumeratedSets
from sage.categories.cartesian_product import cartesian_product
from sage.categories.sets_cat import EmptySetError
from sage.categories.classical_crystals import ClassicalCrystals
from sage.categories.tensor import tensor
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.list_clone import ClonableArray
from sage.structure.parent import Parent
from sage.structure.element_wrapper import ElementWrapper
from sage.misc.inherit_comparison import InheritComparisonClasscallMetaclass
from sage.misc.all import prod
from sage.sets.set import Set, Set_object
from sage.rings.infinity import infinity
from sage.rings.integer_ring import ZZ
from sage.functions.other import binomial
from sage.calculus.var import var

from sage.combinat.words.word import Word
from sage.combinat.subset import Subsets_sk
from sage.combinat.combinat import CombinatorialElement
from sage.combinat.composition import Composition, Compositions
from sage.combinat.permutation import Permutations_mset
from sage.combinat.partition import RegularPartitions_n
from sage.combinat.integer_lists.invlex import IntegerListsLex
from sage.combinat.combinatorial_map import combinatorial_map
from sage.combinat.sf.sf import SymmetricFunctions
from sage.combinat.shuffle import ShuffleProduct, ShuffleProduct_overlapping
from sage.combinat.crystals.letters import CrystalOfLetters as Letters
from sage.combinat.root_system.cartan_type import CartanType

@add_metaclass(InheritComparisonClasscallMetaclass)
class OrderedMultisetPartition(ClonableArray):
    r"""
    Ordered Multiset Partition

    An ordered multiset partition `c` of a multiset `X` is a list
    `[c_1, \ldots, c_r]` of nonempty subsets of `X` (note: not
    sub-multisets), called the blocks of `c`, whose multi-union is `X`.

    EXAMPLES:

    The simplest way to create a ordered multiset partition is by specifying
    its entries as a list, tuple::

        sage: OrderedMultisetPartition([[3],[2,1]])
        [{3}, {1,2}]
        sage: OrderedMultisetPartition(((3,), (1,2)))
        [{3}, {1,2}]
        sage: OrderedMultisetPartition([set([i]) for i in range(2,5)])
        [{2}, {3}, {4}]

    You can also create a ordered multiset partition `c` from a list of positive
    integers and from a list of nonnegative integers. In the former case, each
    integer is given its own block of `c`. In the latter case, zeros separate the
    blocks of `c`::

        sage: OrderedMultisetPartition([i for i in range(2,5)])
        [{2}, {3}, {4}]
        sage: OrderedMultisetPartition([1, 0, 1, 3, 5, 0, 2, 1])
        [{1}, {1,3,5}, {1,2}]
        sage: OrderedMultisetPartition([1, 1, 0, 3, 5, 0, 2, 1])
        Traceback (most recent call last):
        ...
        ValueError: ordered multiset partitions do not have repeated entries
        within blocks ([[1, 1], [3, 5], [2, 1]] received)


    REFERENCES:

    - [HRW2015]_
    - [HRS2016]_
    - [LM2018]_
    """
    @staticmethod
    def __classcall_private__(cls, co):
        """
        Create an ordered multiset partition (i.e., a list of sets) from the passed
        arguments with the appropriate parent.

        EXAMPLES::

            sage: OrderedMultisetPartition([[3], [2,1]])
            [{3}, {1,2}]
            sage: c = OrderedMultisetPartition([2, 3, 4, 5]); c
            [{2}, {3}, {4}, {5}]
            sage: d = OrderedMultisetPartition([1, 0, 1, 3, 5, 0, 2, 1]); d
            [{1}, {1,3,5}, {1,2}]

        TESTS::

            sage: c.parent() == OrderedMultisetPartitions([2,3,4,5])
            True
            sage: d.parent() == OrderedMultisetPartitions([1,1,1,2,3,5])
            True
            sage: repr(OrderedMultisetPartition([]).parent())
            'Ordered Multiset Partitions of multiset {{}}'
        """
        if not co:
            P = OrderedMultisetPartitions([])
            return P.element_class(P, [])
        if isinstance(co[0], (list, tuple, set, frozenset, Set_object)):
            # standard input
            X = _concatenate(co)
            P = OrderedMultisetPartitions(_get_weight(X))
            return P.element_class(P, co)
        else:
            # user shortcuts
            weight = _get_weight(c for c in co if c not in {0, '0'})
            P = OrderedMultisetPartitions_X(tuple(weight.iteritems()))
            return P.element_class(P, P.from_list(co))

    def __init__(self, *args):
        """
        Initialize ``self``.

        EXAMPLES::

            sage: c = OrderedMultisetPartitions(7)([[1,3], [1,2]])
            sage: OrderedMultisetPartition([[1,3], [1,2]]) == c
            True

        TESTS::

            sage: TestSuite(c).run()

            sage: OMP = OrderedMultisetPartition
            sage: c = OMP([[1, 3], [1, 'a', 'b']])
            sage: TestSuite(c).run()

            sage: c = OMP('abc0ab0a')
            sage: TestSuite(c).run()

            sage: OMP([]) == OMP('')
            True
            sage: OMP([1,2,3,1]) == OMP([[1],[2],[3],[1]])
            True
            sage: OMP([1,2,3,0,1]) == OMP([[1,2,3],[1]])
            True
        """
        if len(args) == 1:
            parent = OrderedMultisetPartitions()
        else:
            parent = args[0]
        co = args[-1]
        if co and not isinstance(co[0], (list, tuple, set, frozenset, Set_object)):
            # Assume `co` is a list with (or without) zeros, representing an OMP
            co = parent.from_list(co)
        else:
            # Delte empty blocks
            co = [block for block in co if block]
        ClonableArray.__init__(self, parent, [Set(list(k)) for k in co])
        self._multiset = _get_multiset(co)
        self._weight = _get_weight(self._multiset)
        self._order = sum([len(block) for block in self])
        if all((a in ZZ and a > 0) for a in self._multiset):
            self._n = ZZ(sum(self._multiset))
        else:
            self._n = None

    def check(self):
        """
        Check that we are a valid ordered multiset partition.

        EXAMPLES::

            sage: c = OrderedMultisetPartitions(4)([[1], [1,2]])
            sage: c.check()

            sage: OMPs = OrderedMultisetPartitions()
            sage: c = OMPs([[1], [1], ['a']])
            sage: c.check()

        TESTS::

            sage: c = OMPs([[1, 1], [1, 4]])
            Traceback (most recent call last):
            ...
            AssertionError: cannot convert [[1, 1], [1, 4]] into an element
             of Ordered Multiset Partitions
        """
        if self not in self.parent():
            raise ValueError("{} not an element of {}".format(self, self.parent()))

    def _repr_(self):
        return self._repr_tight()

    def _repr_normal(self):
        # TODO: simplify if/once ``_repr_`` method for ``Set`` sorts its elements.
        string_parts = map(lambda k: str(sorted(k)), self)
        string_parts = ", ".join(string_parts).replace("[","{").replace("]","}")
        return "[" + string_parts + "]"

    def _repr_tight(self):
        repr = self._repr_normal()
        # eliminate spacing within blocks
        return repr.replace(", ", ",").replace("},{", "}, {")

    def __hash__(self):
        """
        Return the hash of ``self``.

        The parent is not included as part of the hash.

        EXAMPLES::

            sage: OMP = OrderedMultisetPartitions(4)
            sage: A = OMP([[1], [1, 2]])
            sage: B = OMP([{1}, {1, 2}])
            sage: hash(A) == hash(B)
            True
        """
        return sum(hash(x) for x in self)

    def __eq__(self, y):
        """
        Check equality of ``self`` and ``y``.

        The parent is not included as part of the equality check.

        EXAMPLES::

            sage: OMP = OrderedMultisetPartitions(4)
            sage: A = OMP([[1], [1, 2]])
            sage: B = OMP([{1}, {3}])
            sage: A == B
            False
            sage: C = OMP([[1,2], [1]])
            sage: A == C
            False
            sage: D = OMP.from_list([1,0,1,2])
            sage: A == D
            True
        """
        if not isinstance(y, OrderedMultisetPartition):
            return False
        return list(self) == list(y)

    def __ne__(self, y):
        """
        Check lack of equality of ``self`` and ``y``.

        The parent is not included as part of the equality check.
        """
        return not (self == y)

    def __add__(self, other):
        """
        Return the concatenation of two ordered multiset partitions.

        This operation represents the product in Hopf algebra of ordered multiset
        partitions in its natural basis [LM2018]_.

        EXAMPLES::

            sage: OrderedMultisetPartition([1,1,3]) + OrderedMultisetPartition([4,1,0,2])
            [{1}, {1}, {3}, {1,4}, {2}]

        TESTS::

            sage: OMP = OrderedMultisetPartition
            sage: OMP([]) + OMP([]) == OMP([])
            True
            sage: OMP([1,0,1,0,3]) + OMP([1,4,0,2]) == OMP([{1}, {1}, {3}, {1,4}, {2}])
            True
        """
        co = list(self) + list(other)
        X = _concatenate(co)
        return OrderedMultisetPartitions(_get_weight(X))(co)

    @combinatorial_map(order=2, name='reversal')
    def reversal(self):
        r"""
        Return the reverse ordered multiset partition of ``self``.

        The reverse of a ordered multiset partition `(B_1, B_2, \ldots, B_k)`
        is defined as the ordered multiset partition `(B_k, B_{k-1}, \ldots, B_1)`.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([1, 0, 1, 3, 0, 2, 3, 4]); C
            [{1}, {1,3}, {2,3,4}]
            sage: C.reversal()
            [{2,3,4}, {1,3}, {1}]
        """
        return self.parent()(list(reversed(self)))

    def shape_from_cardinality(self):
        """
        Return a composition that records the cardinality of each block of ``self``.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([3, 4, 1, 0, 2, 0, 1, 2, 3, 7]); C
            [{1,3,4}, {2}, {1,2,3,7}]
            sage: C.shape_from_cardinality()
            [3, 1, 4]
            sage: OrderedMultisetPartition([]).shape_from_cardinality() == Composition([])
            True
        """
        return Composition([len(k) for k in self])

    def shape_from_size(self):
        """
        Return a composition that records the sum of entries of each block of ``self``.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([3, 4, 1, 0, 2, 0, 1, 2, 3, 7]); C
            [{1,3,4}, {2}, {1,2,3,7}]
            sage: C.shape_from_size()
            [8, 2, 13]

        TESTS::

            sage: OrderedMultisetPartition([]).shape_from_size() == Composition([])
            True
            sage: D = OrderedMultisetPartition([['a', 'b'], ['a']]); D
            [{'a','b'}, {'a'}]
            sage: D.shape_from_size() == None
            True
        """
        if self._n is not None:
            return Composition([sum(k) for k in self])

    def letters(self):
        """
        Return the set of distinct elements occurring within the blocks of ``self``.
        """
        return _union_of_sets(list(self))

    def multiset(self, as_dict=False):
        """
        Return the multiset corresponding to ``self`` as a tuple or as a dictionary.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([3, 4, 1, 0, 2, 0, 1, 2, 3, 7]); C
            [{1,3,4}, {2}, {1,2,3,7}]
            sage: C.multiset()
            (1, 1, 2, 2, 3, 3, 4, 7)
            sage: C.multiset(as_dict=True)
            {1: 2, 2: 2, 3: 2, 4: 1, 7: 1}
            sage: OrderedMultisetPartition([]).multiset() == ()
            True
        """
        if as_dict:
            return self._weight
        else:
            return self._multiset

    def max_letter(self):
        """
        Return the maximum letter appearing in ``self.letters()``.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([3, 4, 1, 0, 2, 0, 1, 2, 3, 7])
            sage: C.max_letter()
            7
            sage: D = OrderedMultisetPartition('abc0ab0a0bcf0cd')
            sage: D.max_letter()
            'f'
        """
        if not self.letters():
            return None
        else:
            return max(self.letters())

    def size(self):
        """
        Return the size of ``self`` (that is, the sum of all integers in all blocks)
        if ``self`` is a list of subsets of positive integers.

        Else, return ``None``.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([3, 4, 1, 0, 2, 0, 1, 2, 3, 7]); C
            [{1,3,4}, {2}, {1,2,3,7}]
            sage: C.size()
            23
            sage: C.size() == sum(k for k in C.shape_from_size())
            True
            sage: OrderedMultisetPartition([[7,1],[3]]).size()
            11

        TESTS::

            sage: OrderedMultisetPartition([]).size() == 0
            True
            sage: OrderedMultisetPartition('ab0abc').size() is None
            True
        """
        return self._n

    def order(self):
        """
        Return the total number of elements in all blocks.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([3, 4, 1, 0, 2, 0, 1, 2, 3, 7]); C
            [{1,3,4}, {2}, {1,2,3,7}]
            sage: C.order()
            8
            sage: C.order() == sum(C.weight().values())
            True
            sage: C.order() == sum(k for k in C.shape_from_cardinality())
            True
            sage: OrderedMultisetPartition([[7,1],[3]]).order()
            3
        """
        return self._order

    def length(self):
        """
        Return the number of blocks.

        EXAMPLES::

            sage: OrderedMultisetPartition([[7,1],[3]]).length()
            2
        """
        return len(self)

    def weight(self, as_weak_comp=False):
        r"""
        Return a dictionary, with keys being the letters in ``self.letters()``
        and values being their (positive) frequency.

        Alternatively, if ``as_weak_comp`` is ``True``, count the number of instances
        `n_i` for each distinct positive integer `i` across all blocks of ``self``.
        Return as a list `[n_1, n_2, n_3, ..., n_k]`, where `k` is the max letter
        appearing in ``self.letters()``.

        EXAMPLES::

            sage: OrderedMultisetPartition([[6,1],[1,3],[1,3,6]]).weight()
            {1: 3, 3: 2, 6: 2}
            sage: OrderedMultisetPartition([[6,1],[1,3],[1,3,6]]).weight(as_weak_comp=True)
            [3, 0, 2, 0, 0, 2]
            sage: OrderedMultisetPartition([]).weight() == {}
            True

        TESTS::

            sage: OrderedMultisetPartition('ab0abc0b0b0c').weight()
            {'a': 2, 'b': 4, 'c': 2}
            sage: OrderedMultisetPartition('ab0abc0b0b0c').weight(as_weak_comp=True)
            Traceback (most recent call last):
            ...
            AssertionError: {'a': 2, 'c': 2, 'b': 4} is not a numeric multiset
        """
        w = self._weight
        if as_weak_comp:
            if all(v in ZZ for v in w):
                w = [w.get(i, 0) for i in range(1,self.max_letter()+1)]
            else:
                raise AssertionError("%s is not a numeric multiset"%w)
        return w

    def deconcatenate(self, k=2):
        r"""
        Return the set of `k`-deconcatenations of ``self``.

        A `k`-tuple `(C_1, \ldots, C_k)` of ordered multiset partitions represents
        a `k`-deconcatenation of an ordered multiset partition `C` if
        `C_1 + \cdots + C_k = C`.

        .. NOTE::

            This is not to be confused with ``self.split()``, which splits each block
            of ``self`` before making `k`-tuples of ordered multiset partitions.

        EXAMPLES::

            sage: OrderedMultisetPartition([[7,1],[3]]).deconcatenate()
            {([{1,7}], [{3}]), ([], [{1,7}, {3}]), ([{1,7}, {3}], [])}
            sage: OrderedMultisetPartition('bc0a').deconcatenate()
            {([], [{'b','c'}, {'a'}]), ([{'b','c'}, {'a'}], []), ([{'b','c'}], [{'a'}])}
            sage: OrderedMultisetPartition('abc0').deconcatenate(3)
            {([{'a','b','c'}], [], []),
             ([], [{'a','b','c'}], []),
             ([], [], [{'a','b','c'}])}

        TESTS::

            sage: C = OrderedMultisetPartition('abcde'); C
            [{'a'}, {'b'}, {'c'}, {'d'}, {'e'}]
            sage: all( C.deconcatenate(k).cardinality()
            ....:      == binomial(C.length() + k-1, k-1)
            ....:      for k in range(1, 5) )
            True
        """
        P = OrderedMultisetPartitions(alphabet=self.letters(),max_length=self.length())
        out = []
        for c in IntegerListsLex(self.length(), length=k):
            ps = [sum(c[:i]) for i in range(k+1)]
            out.append(tuple([P(self[ps[i]:ps[i+1]]) for i in range(len(ps)-1)]))
        return Set(out)

    def split(self, k=2):
        r"""
        Return the set of `k`-splittings of ``self``.

        A `k`-tuple `(A^1, \ldots, A^k)` of ordered multiset partitions represents
        a `k`-splitting of an ordered multiset partition `A=[b_1, \ldots, b_r]` if
        one can express each block `b_i` as an (ordered) disjoint union of sets
        `b_i = b^1_i \sqcup \cdots \sqcup b^k_i` (some possibly empty) so that
        each `A^j` is the ordered multiset partition corresponding to the list
        `[b^j_1, b^j_2, \ldots, b^j_r]`, excising empty sets appearing therein.

        This operation represents the coproduct in Hopf algebra of ordered multiset
        partitions in its natural basis [LM]_.

        EXAMPLES::

            sage: sorted(OrderedMultisetPartition([[1,2],[4]]).split())
            [([], [{1,2}, {4}]), ([{2}, {4}], [{1}]), ([{1,2}], [{4}]),
             ([{4}], [{1,2}]), ([{1}], [{2}, {4}]), ([{1}, {4}], [{2}]),
             ([{2}], [{1}, {4}]), ([{1,2}, {4}], [])]
            sage: sorted(OrderedMultisetPartition([[1,2]]).split(3))
            [([], [], [{1,2}]), ([], [{2}], [{1}]), ([], [{1}], [{2}]),
             ([], [{1,2}], []), ([{2}], [{1}], []), ([{1}], [], [{2}]),
             ([{1}], [{2}], []), ([{2}], [], [{1}]), ([{1,2}], [], [])]

        TESTS::

            sage: C = OrderedMultisetPartition([1,2,0,4,5,6]); C
            [{1,2}, {4,5,6}]
            sage: C.split().cardinality() == 2**len(C[0]) * 2**len(C[1])
            True
            sage: C.split(3).cardinality() == (1+2)**len(C[0]) * (1+2)**len(C[1])
            True
            sage: C = OrderedMultisetPartition([])
            sage: C.split(3) == Set([(C, C, C)])
            True
        """
        P = OrderedMultisetPartitions(alphabet=self.letters(),max_length=self.length())

        # corner case
        if not self:
            return Set([tuple([self]*k)])
        else:
            out = set()
            tmp = cartesian_product([_split_block(block, k) for block in self])
            for t in tmp:
                out.add(tuple([P([k for k in c if len(k)>0]) for c in zip(*t)]))
            return Set(out)

    def finer(self, strong=False):
        """
        Return the set of ordered multiset partitions that are finer than ``self``.

        An ordered multiset partition `A` is finer than another `B` if,
        reading left-to-right, every block of `B` is the union of some consecutive
        blocks of `A`.

        If optional argument ``strong`` is set to ``True``, then return only those
        `A` whose blocks are deconcatenations of blocks of `B`. (Here, we view
        blocks of `B` as sorted lists instead of sets.)


        EXAMPLES::

            sage: C = OrderedMultisetPartition([[3,2]]).finer()
            sage: C.cardinality()
            3
            sage: C.list()
            [[{2}, {3}], [{2,3}], [{3}, {2}]]
            sage: OrderedMultisetPartition([]).finer()
            {[]}
            sage: O = OrderedMultisetPartitions([1, 1, 'a', 'b'])
            sage: o = O.an_element()
            sage: o.finer()
            {[{'b'}, {'a'}, {1}, {1}], [{'a'}, {'b'}, {1}, {1}], [{'a','b'}, {1}, {1}]}
            sage: o.finer() & o.fatter() == Set([o])
            True
        """
        P = OrderedMultisetPartitions(self._multiset)

        if not self:
            return Set([self])
        else:
            tmp = cartesian_product([_refine_block(block, strong) for block in self])
            return Set([P(_concatenate(map(list,c))) for c in tmp])

    def is_finer(self, co):
        """
        Return ``True`` if the ordered multiset partition ``self`` is finer than the
        composition ``co``; otherwise, return ``False``.

        EXAMPLES::

            sage: OrderedMultisetPartition([[4],[1],[2]]).is_finer([[1,4],[2]])
            True
            sage: OrderedMultisetPartition([[1],[4],[2]]).is_finer([[1,4],[2]])
            True
            sage: OrderedMultisetPartition([[1,4],[1],[1]]).is_finer([[1,4],[2]])
            False
        """
        X = _concatenate(co)
        if self.weight() != OrderedMultisetPartitions(_get_weight(X))(co).weight():
            return False

        # trim common prefix and suffix to make the search-space smaller
        co1 = map(Set,self)
        co2 = map(Set,co)
        while co1[0] == co2[0]:
            co1 = co1[1:]; co2 = co2[1:]
        while co1[-1] == co2[-1]:
            co1 = co1[:-1]; co2 = co2[:-1]

        co1 = OrderedMultisetPartition(co1)
        co2 = OrderedMultisetPartition(co2)
        return co1 in co2.finer()

    def fatten(self, grouping):
        """
        Return the ordered multiset partition fatter than ``self``, obtained by
        grouping together consecutive parts according to ``grouping`` (whenever
        this does not violate the strictness condition).

        INPUT:

        - ``grouping`` -- a composition (or list) whose sum is the length of ``self``

        EXAMPLES:

        Let us start with the composition::

            sage: C = OrderedMultisetPartition([4,1,5,0,2,0,7,1]); C
            [{1,4,5}, {2}, {1,7}]

        With ``grouping`` equal to `(1, 1, 1)`, `C` is left unchanged::

            sage: C.fatten([1,1,1])
            [{1,4,5}, {2}, {1,7}]

        With ``grouping`` equal to `(2,1)` or `(1,2)`, a union of consecutive parts
        is achieved::

            sage: C.fatten([2,1])
            [{1,2,4,5}, {1,7}]
            sage: C.fatten([1,2])
            [{1,4,5}, {1,2,7}]

        However, the ``grouping`` `(3)` will throw an error, as `1` cannot appear twice
        in any block of ``C``::

            sage: C.fatten(Composition([3]))
            Traceback (most recent call last):
            ...
            ValueError: [{1,4,5,2,1,7}] is not a valid ordered multiset partition
        """
        if sum(list(grouping)) != self.length():
            raise ValueError("%s is not a composition of ``self.length()`` (=%s)"%(grouping, self.length()))

        valid = True
        result = []
        for i in range(len(grouping)):
            result_i = self[sum(grouping[:i]) : sum(grouping[:i+1])]
            # check that grouping[i] is allowed, i.e., `|A\cup B| = |A| + |B|`
            strict_size = sum(map(len,result_i))
            size = len(_union_of_sets(result_i))
            if size < strict_size:
                valid = False
            result.append(_concatenate(result_i))
        if not valid:
            str_rep = '['
            for i in range(len(grouping)):
                st = ",".join(str(k) for k in result[i])
                str_rep += "{" + st+ "}"
            str_rep = str_rep.replace("}{", "}, {") + "]"
            raise ValueError("%s is not a valid ordered multiset partition"%(str_rep))
        else:
            return OrderedMultisetPartitions(self._multiset)(result)

    def fatter(self):
        """
        Return the set of ordered multiset partitions which are fatter than ``self``.

        An ordered multiset partition `A` is fatter than another `B` if, reading
        left-to-right, every block of `A` is the union of some consecutive blocks
        of `B`.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([{1,4,5}, {2}, {1,7}]).fatter()
            sage: C.cardinality()
            3
            sage: list(C)
            [[{1,4,5}, {2}, {1,7}], [{1,4,5}, {1,2,7}], [{1,2,4,5}, {1,7}]]
            sage: list(OrderedMultisetPartition([['a','b'],['c'],['a']]).fatter())
            [[{'a','b'}, {'a','c'}], [{'a','b','c'}, {'a'}], [{'a','b'}, {'c'}, {'a'}]]

        Some extreme cases::

            sage: list(OrderedMultisetPartition('abc0').fatter())
            [[{'a','b','c'}]]
            sage: list(OrderedMultisetPartition([]).fatter())
            [[]]
            sage: OrderedMultisetPartition([1,2,3,4]).fatter().issubset(OrderedMultisetPartition([[1,2,3,4]]).finer())
            True
        """
        out = set()
        for c in Compositions(self.length()):
            try:
                out.add(self.fatten(c))
            except ValueError:
                pass
        return Set(out)


    def minimaj(self):
        """
        Return the minimaj statistic on ordered multiset partitions.

        We define `minimaj` via an example:

        1. Sort the block in ``self`` as prescribed by ``self.minimaj_word()``,
           keeping track of the original separation into blocks.
           - in:   [{1,5,7}, {2,4}, {5,6}, {4,6,8}, {1,3}, {1,2,3}]
           - out:  ( 5,7,1 /  2,4 /  5,6 /  4,6,8 /  3,1 /  1,2,3 )

        2. Record the indices where descents in this word occur.
           - word:      (5, 7, 1 / 2, 4 / 5, 6 / 4, 6, 8 / 3, 1 / 1, 2, 3)
           - indices:    1  2  3   4  5   6  7   8  9 10  11 12  13 14 15
           - descents:  {   2,               7,       10, 11             }

        3. Compute the sum of the descents
           - minimaj = 2 + 7 + 10 + 11 = 30

        REFERENCES:

        - [HRW2015]_

        EXAMPLES::

            sage: C = OrderedMultisetPartition([{1,5,7}, {2,4}, {5,6}, {4,6,8}, {1,3}, {1,2,3}])
            sage: C, C.minimaj_word()
            ([{1,5,7}, {2,4}, {5,6}, {4,6,8}, {1,3}, {1,2,3}],
             (5, 7, 1, 2, 4, 5, 6, 4, 6, 8, 3, 1, 1, 2, 3))
            sage: C.minimaj()
            30
            sage: C = OrderedMultisetPartition([{2,4}, {1,2,3}, {1,6,8}, {2,3}])
            sage: C, C.minimaj_word()
            ([{2,4}, {1,2,3}, {1,6,8}, {2,3}], (2, 4, 1, 2, 3, 6, 8, 1, 2, 3))
            sage: C.minimaj()
            9
            sage: OrderedMultisetPartition([]).minimaj()
            0
            sage: C = OrderedMultisetPartition('bd0abc0b')
            sage: C, C.minimaj_word()
            ([{'b','d'}, {'a','b','c'}, {'b'}], ('d', 'b', 'c', 'a', 'b', 'b'))
            sage: C.minimaj()
            4
        """
        D = _descents(self.minimaj_word())
        return sum(D) + len(D)

    def minimaj_word(self):
        """
        Return an ordering of ``self._multiset`` derived from the minimaj ordering
        on blocks of ``self``.

        .. SEEALSO::

            :meth:`OrderedMultisetPartition.minimaj_blocks()`.

        EXAMPLES::

            sage: C = OrderedMultisetPartition([2,1,0,1,2,3,0,1,2,0,3,0,1]); C
            [{1,2}, {1,2,3}, {1,2}, {3}, {1}]
            sage: C.minimaj_blocks()
            ((1, 2), (2, 3, 1), (1, 2), (3,), (1,))
            sage: C.minimaj_word()
            (1, 2, 2, 3, 1, 1, 2, 3, 1)
        """
        return _concatenate(self.minimaj_blocks())

    def minimaj_blocks(self):
        r"""
        Return the minimaj ordering on blocks of ``self``.

        We define the ordering via the example below.

        Sort the blocks `[B_1,...,B_k]` of ``self`` from right to left via:

        1. Sort the last block `B_k` in increasing order, call it the word `W_k`

        2. If blocks `B_{i+1}, \ldots, B_k` have been converted to words
           `W_{i+1}, \ldots, W_k`, use the letters in `B_i` to make the unique
           word `W_i` that has a factorization `W_i=(u,v)` satisfying:
           - letters of `u` and `v` appear in increasing order, with `v` possibly empty
           - letters in `vu` appear in increasing order
           - ``v[-1]`` is the largest letter `a \in B_i` satisfying ``a <= W_{i+1}[0]``

        EXAMPLES::

            sage: OrderedMultisetPartition([1,5,7,0,2,4,0,5,6,0,4,6,8,0,1,3,0,1,2,3])
            [{1,5,7}, {2,4}, {5,6}, {4,6,8}, {1,3}, {1,2,3}]
            sage: _.minimaj_blocks()
            ((5, 7, 1), (2, 4), (5, 6), (4, 6, 8), (3, 1), (1, 2, 3))
            sage: OrderedMultisetPartition([]).minimaj_blocks()
            ()
        """
        if len(self) == 0:
            return ()

        C = [sorted(self[-1])]
        for i in range(1,len(self)):
            lower = []; upper = []
            for j in self[-1-i]:
                if j <= C[0][0]:
                    lower.append(j)
                else:
                    upper.append(j)
            C = [sorted(upper)+sorted(lower)] + C
        return tuple(map(tuple,C))

    def to_tableau(self):
        r"""
        Return a sequence of lists corresponding to row words of (skew-)tableaux.

        Output is the minimaj bijection `\varphi` of Benkart, et al. applied to ``self``.

        .. TODO::

            Implement option for mapping to sequence of (skew-)tableaux?

        REFERENCES:

        - [BCHOPSY2017]_

        EXAMPLES::

            sage: co = ((1,2,4),(4,5),(3,),(4,6,1),(2,3,1),(1,),(2,5))
            sage: OrderedMultisetPartition(co).to_tableau()
            [[5, 1], [3, 1], [6], [5, 4, 2], [1, 4, 3, 4, 2, 1, 2]]
        """
        if not self:
            return []
        bb = self.minimaj_blocks()
        b = [block[0] for block in bb]
        beginning = _partial_sum(self.shape_from_cardinality())
        w = _concatenate(bb)
        D = [0] + _descents(w) + [len(w)]
        pieces = [b]
        for i in range(len(D)-1):
            p = [w[j] for j in range(D[i]+1,D[i+1]+1) if j not in beginning]
            pieces = [p[::-1]] + pieces
        return pieces

    def major_index(self):
        r"""
        Return the major index of ``self``.

        The major index is a statistic on ordered multiset partitions, which
        we define here via an example.

        1. Sort each block in the list ``self`` in descending order to create
           a word `w`, keeping track of the original separation into blocks:

           - in:  [{3,4,5}, {2,3,4}, {1}, {4,5}]
           - out: [ 5,4,3 /  4,3,2 /  1 /  5,4 ]

        2. Create a sequence `v = (v_0, v_1, v_2, \ldots)`  of length
           ``self.order()+1``, built recursively by:

           - `v_0 = 0`
           - `v_j = v_{j-1} + \delta(j)`, where `\delta(j) = 1` if `j` is
             the index of an end of a block, and zero otherwise.

             * in:    [ 5,4,3 /  4,3,2 /  1 /  5,4]
             * out: (0, 0,0,1,   1,1,2,   3,   3,4)

        3. Compute `\sum_j v_j`, restricted to descent positions in `w`, i.e.,
           sum over those `j` with `w_j > w_{j+1}`:

           - in:  w:   [5, 4, 3, 4, 3, 2, 1, 5, 4]
                  v: (0 0, 0, 1, 1, 1, 2, 3, 3, 4)
           - maj :=     0 +0    +1 +1 +2    +3     = 7

        REFERENCES:

        - [HRW2015]_

        EXAMPLES::

            sage: C = OrderedMultisetPartition([{1,5,7}, {2,4}, {5,6}, {4,6,8}, {1,3}, {1,2,3}])
            sage: C.major_index()
            27
            sage: C = OrderedMultisetPartition([{3,4,5}, {2,3,4}, {1}, {4,5}])
            sage: C.major_index()
            7
        """
        ew = [enumerate(sorted(k)) for k in self]
        w = []
        v = [0]
        for eblock in ew:
            for (i,wj) in sorted(eblock, reverse=True):
                vj = v[-1]
                if i == 0:
                    vj += 1
                v.append(vj)
                w.append(wj)
        maj = [v[j+1] for j in range(len(w)-1) if w[j] > w[j+1]]
        return sum(maj)

    def shuffle_product(self, other, overlap=False):
        r"""
        Return the shuffles (with multiplicity) of blocks of ``self``
        with blocks of ``other``.

        In case optional argument ``overlap`` is ``True``, instead return the allowable
        overlapping shuffles. An overlapping shuffle `C` is allowable if, whenever one
        of its blocks `c` comes from the union `c = a \cup b` of a block of ``self``
        and a block of ``other``, then this union is disjoint.

        .. SEEALSO::

            :meth:`Composition.shuffle_product()`

        EXAMPLES::

            sage: A = OrderedMultisetPartition([2,1,3,0,1,2]); A
            [{1,2,3}, {1,2}]
            sage: B = OrderedMultisetPartition([[3,4]]); B
            [{3,4}]
            sage: C = OrderedMultisetPartition([[4,5]]); C
            [{4,5}]
            sage: list(A.shuffle_product(B))
            [[{1,2,3}, {1,2}, {3,4}], [{3,4}, {1,2,3}, {1,2}], [{1,2,3}, {3,4}, {1,2}]]
            sage: list(A.shuffle_product(B, overlap=True))
            [[{1,2,3}, {1,2}, {3,4}], [{1,2,3}, {3,4}, {1,2}],
             [{3,4}, {1,2,3}, {1,2}], [{1,2,3}, {1,2,3,4}]]
            sage: list(A.shuffle_product(C, overlap=True))
            [[{1,2,3}, {1,2}, {4,5}], [{1,2,3}, {4,5}, {1,2}], [{4,5}, {1,2,3}, {1,2}],
             [{1,2,3,4,5}, {1,2}], [{1,2,3}, {1,2,4,5}]]
        """
        other = OrderedMultisetPartition(other)
        P = OrderedMultisetPartitions(self._multiset + other._multiset)
        if not overlap:
            for term in ShuffleProduct(self, other, element_constructor=P):
                yield term
        else:
            A = map(tuple, self); B = map(tuple, other)
            for term in ShuffleProduct_overlapping(A, B):
                if len(_concatenate(map(Set, term))) == len(P._Xtup):
                    yield P(term)

    # A sorting scheme.
    # An alternative to that served up by ``OrderedMultisetPartitions().__iter__()``
    def soll_gt(self, other):
        """
        Return ``True`` if the composition ``self`` is greater than the
        composition ``other`` with respect to the soll-ordering; otherwise,
        return ``False``.

        The soll-ordering is a total order on the set of all ordered multiset partitions.
        ("soll" is short for "size, order, length, lexicographic".)

        An ordered multiset partition `I` is greater than an ordered multiset partition
        `J` if and only if one of the following conditions holds:

        - The size of `I` is greater than size of `J`. (Recall size of `I` is ``None``
          if `I` is not numeric.)

        - The sizes of `I` and `J` are equal, and the order of `I` is
          greater than the order of `J`.

        - The sizes and orders of `I` and `J` coincide, but the length of `I`
          is greater than the length of `J`.

        - The sizes/orders/lengths of `I` and `J` coincide, but `I` is lexicographically
          greater than `J`. (Here, lexicographic order is taken with respect to blocks,
          not entries within the blocks.)

        EXAMPLES::

            sage: C = OrderedMultisetPartition([2,1,0,1,2,3,0,1,2,0,3,0,1])
            sage: D1 = OrderedMultisetPartition([2,4,0,2,3])
            sage: D2 = OrderedMultisetPartition([{1,2}, {1,2,3}, {1,2}, {1}, {1,2}])
            sage: D3 = OrderedMultisetPartition([1,0,1,2,3,0,1,2,3,0,1,2])
            sage: D4 = OrderedMultisetPartition([1,2,0,2,3,0,1,3,0,1,2,0,1])
            sage: C.soll_gt(D1) #size
            True
            sage: C.soll_gt(D2) #order
            False
            sage: C.soll_gt(D3) #length
            True
            sage: C.soll_gt(D4) #lex
            True

        TESTS::

            sage: C = OrderedMultisetPartition('ba0abc0ab0c0a')
            sage: D2 = OrderedMultisetPartition('ab0abc0ab0a0ab')
            sage: D3 = OrderedMultisetPartition('a0abc0abc0ab')
            sage: D4 = OrderedMultisetPartition('ab0bc0ac0ab0a')
            sage: C.soll_gt(D2) #order
            False
            sage: C.soll_gt(D3) #length
            True
            sage: C.soll_gt(D4) #lex
            False
        """
        co1 = self
        co2 = OrderedMultisetPartition(other)
        # check size
        if (co1).size() > (co2).size():
            return True
        elif (co1).size() < (co2).size():
            return False
        # check order
        if (co1).order() > (co2).order():
            return True
        elif (co1).order() < (co2).order():
            return False
        # check length
        if (co1).length() > (co2).length():
            return True
        if (co1).length() < (co2).length():
            return False
        # check lex.
        if co1._n and co2._n:
            # give preference to blocks with larger sum
            co1 = [Word([sum(k)]+sorted(k)) for k in co1]
            co2 = [Word([sum(k)]+sorted(k)) for k in co2]
        else:
            w1 = [Word(map(str, sorted(k))) for k in co1]
            w2 = [Word(map(str, sorted(k))) for k in co2]
        return w1 > w2

##############################################################

class OrderedMultisetPartitions(UniqueRepresentation, Parent):
    r"""
    Ordered Multiset Partitions

    An ordered multiset partition `c` of a multiset `X` is a list of nonempty subsets
    (not multisets), called the *blocks* of `c`, whose multi-union is `X`.

    The number of blocks of `c` is called its *length*. The *order* of `c` is the
    cardinality of the multiset `X`. If, additionally, `X` is a multiset of positive
    integers, then the *size* of `c` represents the sum of all elements of `X`.

    The user may wish to focus on ordered multiset partitions of a given size, or
    over a given alphabet. Hence, this class allows a variety of arguments as input.

    INPUT:

    Expects one or two arguments, with different behaviors resulting:
    - One Argument:
        + `X` -- a dictionary (representing a multiset for `c`),
                  or an integer (representing the size of `c`)
    - Two Arguments:
        + `alph` -- a list (representing allowable letters within blocks of `c`),
                    or a positive integer (representing the maximal allowable letter)
        + `ord`  -- a nonnegative integer (the total number of letters within `c`)

    Optional keyword arguments are as follows:
    (See corresponding methods in see :class:`OrderedMultisetPartition` for more details.)

    - ``weight=X``     (list or dictionary `X`) specifies the multiset for `c`
    - ``size=n``       (integer `n`) specifies the size of `c`
    - ``alphabet=S``   (iterable `S`) specifies allowable elements for the blocks of `c`
    - ``length=k``     (integer `k`) specifies the number of blocks in the partition
    - ``min_length=k`` (integer `k`) specifies minimum number of blocks in the partition
    - ``max_length=k`` (integer `k`) specifies maximum number of blocks in the partition
    - ``order=n``      (integer `n`) specifies the cardinality of the multiset that `c` partitions
    - ``min_order=n``  (integer `n`) specifies minimum number of elements in the partition
    - ``max_order=n``  (integer `n`) specifies maximum number of elements in the partition

    EXAMPLES:

    Passing one argument to ``OrderedMultisetPartitions``:

    There are 5 ordered multiset partitions of the multiset `\{\{1, 1, 4\}\}`::

        sage: OrderedMultisetPartitions([1,1,4]).cardinality()
        5

    Here is the list of them::

        sage: OrderedMultisetPartitions([1,1,4]).list()
        [[{1}, {1}, {4}], [{1}, {1,4}], [{1}, {4}, {1}], [{1,4}, {1}], [{4}, {1}, {1}]]

    By chance, there are also 5 ordered multiset partitions of the integer 3::

        sage: OrderedMultisetPartitions(3).cardinality()
        5

    Here is the list of them::

        sage: OrderedMultisetPartitions(3).list()
        [[{3}], [{1,2}], [{2}, {1}], [{1}, {2}], [{1}, {1}, {1}]]

    Passing two argument to ``OrderedMultisetPartitions``:

    There are also 5 ordered multiset partitions of order 2 over the alphabet `\{1, 4\}`::

        sage: OrderedMultisetPartitions([1, 4], 2)
        Ordered Multiset Partitions of order 2 over alphabet {1, 4}
        sage: OrderedMultisetPartitions([1, 4], 2).cardinality()
        5

    Here is the list of them:

        sage: OrderedMultisetPartitions([1, 4], 2).list()
        [[{1,4}], [{1}, {1}], [{1}, {4}], [{4}, {1}], [{4}, {4}]]

    If no arguments are passed to ``OrderedMultisetPartitions``, then the code returns
    the combinatorial class of all ordered multiset partitions::

        sage: OrderedMultisetPartitions()
        Ordered Multiset Partitions
        sage: [] in OrderedMultisetPartitions()
        True
        sage: [[2,3], [1]] in OrderedMultisetPartitions()
        True
        sage: [['a','b'], ['a']] in OrderedMultisetPartitions()
        True
        sage: [[-2,3], [3]] in OrderedMultisetPartitions()
        True
        sage: [[2], [3,3]] in OrderedMultisetPartitions()
        False

    The following examples show how to test whether or not an object
    is an ordered multiset partition::

        sage: [[3,2],[2]] in OrderedMultisetPartitions()
        True
        sage: [[3,2],[2]] in OrderedMultisetPartitions(7)
        True
        sage: [[3,2],[2]] in OrderedMultisetPartitions([2,2,3])
        True
        sage: [[3,2],[2]] in OrderedMultisetPartitions(5)
        False

    Specifying optional arguments:

    - The options ``length``, ``min_length``, and ``max_length`` can be used
      to set length constraints on the ordered multiset partitions. For example, the
      ordered multiset partitions of 4 of length equal to, at least, and at most 2 are
      given by::

        sage: OrderedMultisetPartitions(4, length=2).list()
        [[{3}, {1}], [{1,2}, {1}], [{2}, {2}], [{1}, {3}], [{1}, {1,2}]]
        sage: OrderedMultisetPartitions(4, min_length=3).list()
        [[{2}, {1}, {1}], [{1}, {2}, {1}], [{1}, {1}, {2}], [{1}, {1}, {1}, {1}]]
        sage: OrderedMultisetPartitions(4, max_length=2).list()
        [[{4}], [{1,3}], [{3}, {1}], [{1,2}, {1}], [{2}, {2}], [{1}, {3}], [{1}, {1,2}]]

    - The option ``alphabet`` constrains which integers appear across all blocks of
      the ordered multiset partition. For example, the ordered multiset partitions of 4
      are listed for different choices of alphabet below. Note that ``alphabet``
      is allowed to be an integer or an iterable::

        sage: OMPs = OrderedMultisetPartitions
        sage: OMPs(4, alphabet=3).list()
        [[{1,3}], [{3}, {1}], [{1,2}, {1}], [{2}, {2}], [{2}, {1}, {1}], [{1}, {3}],
         [{1}, {1,2}], [{1}, {2}, {1}], [{1}, {1}, {2}], [{1}, {1}, {1}, {1}]]
        sage: OMPs(4, alphabet=3) == OMPs(4, alphabet=[1,2,3])
        True
        sage: OMPs(4, alphabet=[3]).list()
        []
        sage: OMPs(4, alphabet=[1,3]).list()
        [[{1,3}], [{3}, {1}], [{1}, {3}], [{1}, {1}, {1}, {1}]]
        sage: OMPs(4, alphabet=[2]).list()
        [[{2}, {2}]]
        sage: OMPs(4, alphabet=[1,2]).list()
        [[{1,2}, {1}], [{2}, {2}], [{2}, {1}, {1}], [{1}, {1,2}],
         [{1}, {2}, {1}], [{1}, {1}, {2}], [{1}, {1}, {1}, {1}]]
        sage: OMPs(4, alphabet=4).list() == OMPs(4).list()
        True

    - The option ``weight`` specifies which multiset `X` is to be considered, if it was
      not passed as one of the required arguments for ``OrderedMultisetPartitions``.
      In principle, it is a dictionary, but weak compositions are also allowed.
      For example, the ordered multiset partitions of 4 are listed by weight below::

        sage: OrderedMultisetPartitions(4, weight=[0,0,0,1])
        Ordered Multiset Partitions of integer 4 with constraint: weight={4: 1}
        sage: OrderedMultisetPartitions(4, weight=[0,0,0,1]).list()
        [[{4}]]
        sage: OrderedMultisetPartitions(4, weight=[1,0,1]).list()
        [[{1,3}], [{1}, {3}], [{3}, {1}]]
        sage: OrderedMultisetPartitions(4, weight=[0,2]).list()
        [[{2}, {2}]]
        sage: OrderedMultisetPartitions(4, weight=[0,1,1]).list()
        []
        sage: OrderedMultisetPartitions(4, weight=[2,1]).list()
        [[{1}, {1,2}], [{1}, {1}, {2}], [{1,2}, {1}], [{1}, {2}, {1}], [{2}, {1}, {1}]]
        sage: O1 = OrderedMultisetPartitions(weight=[2,0,1])
        sage: O2 = OrderedMultisetPartitions(weight={1:2, 3:1})
        sage: O1 == O2
        True
        sage: OrderedMultisetPartitions(4, weight=[4]).list()
        [[{1}, {1}, {1}, {1}]]

      This option is ignored if a multiset `X` is passed as a required argument::

        sage: OrderedMultisetPartitions([1,4], weight={1:3, 2:1}).list()
        [[{1}, {4}], [{1,4}], [{4}, {1}]]

    - The (max/min) ``order`` options place constraints on ordered multiset partitions
      when the multiset `X` is not given as required argument or via the ``weight``
      keyword. The ordered multiset partitions of integer 4 are listed by order below::

        sage: OrderedMultisetPartitions(4, order=1).list()
        [[{4}]]
        sage: OrderedMultisetPartitions(4, order=2).list()
        [[{1,3}], [{3}, {1}], [{2}, {2}], [{1}, {3}]]
        sage: OrderedMultisetPartitions(4, order=3).list()
        [[{1,2}, {1}], [{2}, {1}, {1}], [{1}, {1,2}], [{1}, {2}, {1}], [{1}, {1}, {2}]]
        sage: OrderedMultisetPartitions(4, order=4).list()
        [[{1}, {1}, {1}, {1}]]

      And here is a use of ``max_order``, giving the ordered multiset partitions of
      integer 4 with order 1 or 2::

        sage: OrderedMultisetPartitions(4, max_order=2).list()
        [[{4}], [{1,3}], [{3}, {1}], [{2}, {2}], [{1}, {3}]]

      An explicit use of keyword ``order`` is ignored if the order is also implicitly
      provided by the user via other required (or keyword argument ``weight``). In
      each example below, the order must be 3, so the call ``order=2`` is ignored::

        sage: OrderedMultisetPartitions([1,1,4], order=2).list()
        [[{1}, {1}, {4}], [{1}, {1,4}], [{1}, {4}, {1}], [{1,4}, {1}], [{4}, {1}, {1}]]
        sage: OrderedMultisetPartitions([1,4], 3, order=2).list()
        [[{1,4}, {1}], [{1,4}, {4}], [{1}, {1,4}], [{4}, {1,4}], [{1}, {1}, {1}],
         [{1}, {1}, {4}], [{1}, {4}, {1}], [{1}, {4}, {4}], [{4}, {1}, {1}],
         [{4}, {1}, {4}], [{4}, {4}, {1}], [{4}, {4}, {4}]]
        sage: OrderedMultisetPartitions(6, weight=[2,0,0,1], order=2).list()
        [[{1}, {1}, {4}], [{1}, {1,4}], [{1}, {4}, {1}], [{1,4}, {1}], [{4}, {1}, {1}]]

    TESTS::

        sage: C = OrderedMultisetPartitions(8, length=3); C.cardinality()
        72
        sage: C == loads(dumps(C))
        True
    """
    @staticmethod
    def __classcall_private__(self, *args, **constraints):
        """
        Return the correct parent based upon the input:

            * :class:`OrderedMultisetPartitions_all_constraints`
            * :class:`OrderedMultisetPartitions_X`
            * :class:`OrderedMultisetPartitions_X_constraints`
            * :class:`OrderedMultisetPartitions_n`
            * :class:`OrderedMultisetPartitions_n_constraints`
            * :class:`OrderedMultisetPartitions_A`
            * :class:`OrderedMultisetPartitions_A_constraints`

        EXAMPLES::

            sage: OrderedMultisetPartitions()
            Ordered Multiset Partitions
            sage: OrderedMultisetPartitions(4)
            Ordered Multiset Partitions of integer 4
            sage: OrderedMultisetPartitions(4, max_order=2)
            Ordered Multiset Partitions of integer 4 with constraint: max_order=2

            sage: OrderedMultisetPartitions({1:2, 3:1})
            Ordered Multiset Partitions of multiset {{1, 1, 3}}
            sage: OrderedMultisetPartitions({1:2, 3:1}) == OrderedMultisetPartitions([1,1,3])
            True
            sage: OrderedMultisetPartitions({'a':2, 'c':1}, length=2)
            Ordered Multiset Partitions of multiset {{a, a, c}} with constraint: length=2
            sage: OrderedMultisetPartitions({'a':2, 'c':1}, length=4).list()
            []

            sage: OrderedMultisetPartitions(4, 3)
            Ordered Multiset Partitions of order 3 over alphabet {1, 2, 3, 4}
            sage: OrderedMultisetPartitions(['a', 'd'], 3)
            Ordered Multiset Partitions of order 3 over alphabet {a, d}
            sage: OrderedMultisetPartitions([2,4], 3, min_length=2)
            Ordered Multiset Partitions of order 3 over alphabet {2, 4}
             with constraint: min_length=2
        """
        constraints = dict(constraints)
        if "weight" in constraints:
            # Should be a 'dictionary' of letter-frequencies, but accept a weak composition
            w = constraints["weight"]
            if not isinstance(w, dict):
                # make sure we didn't receive ``some_dict.iteritems()``
                if len(w) > 0 and isinstance(w[0], (list, tuple)):
                    w = dict(w)
                else:
                    w = {i+1:w[i] for i in range(len(w)) if w[i] > 0}
            if not all((a in ZZ and a > 0) for a in w.values()):
                raise ValueError("%s must be a dictionary of letter-frequencies or a weak composition"%w)
            else:
                constraints["weight"] = tuple(w.iteritems())

        if "alphabet" in constraints:
            A = constraints["alphabet"]
            if A in ZZ:
                A = range(1,A+1)
            constraints["alphabet"] = Set(A)

        if len(args) == 2: # treat as `alphabet` & `order`
            alph = args[0]; ord = args[1]
            if alph in ZZ:
                alph = range(1,alph+1)
            if (alph and len(Set(alph)) == len(alph)) and (ord in ZZ and ord >= 0):
                constraints.pop("alphabet", None)
                constraints.pop("order", None)
                if constraints == {}:
                    return OrderedMultisetPartitions_A(Set(alph), ord)
                else:
                    return OrderedMultisetPartitions_A_constraints(Set(alph), ord, **constraints)
            elif Set(alph) == Set([]) and ord == 0:
                return OrderedMultisetPartitions_A_constraints(Set(alph), ord, **constraints)
            else:
                raise ValueError("alphabet=%s must be a nonempty set and order=%s must be a nonnegative integer"%(alph,ord))

        elif len(args) == 1: # treat as `size` or `multiset`
            X = args[0]
            if isinstance(X, (list, tuple)):
                tmp = {}
                for i in X:
                    tmp[i] = tmp.get(i, 0) + 1
                X = tmp
            if isinstance(X, dict):
                constraints.pop("size", None)
                constraints.pop("weight", None)
                constraints.pop("alphabet", None)
                constraints.pop("order", None)
                X_items = tuple(X.iteritems())
                if constraints == {}:
                    return OrderedMultisetPartitions_X(X_items)
                else:
                    return OrderedMultisetPartitions_X_constraints(X_items, **constraints)

            elif X in ZZ and X >= 0:
                constraints.pop("size", None)
                if constraints == {}:
                    return OrderedMultisetPartitions_n(X)
                else:
                    return OrderedMultisetPartitions_n_constraints(X, **constraints)

            else:
                raise ValueError("%s must be a nonnegative integer or a list or dictionary representing a multiset"%X)

        else: # generic parent
            return OrderedMultisetPartitions_all_constraints(**constraints)

    def __init__(self, is_finite=None, **constraints):
        """
        Initialize ``self``.
        """
        constraints = dict(constraints)

        # standardize values for certain keywords
        if "alphabet" in constraints:
            if constraints["alphabet"] in ZZ:
                constraints["alphabet"] = Set(range(1, constraints["alphabet"]+1))
            else:
                constraints["alphabet"] = Set(constraints["alphabet"])

        if "weight" in constraints:
            X = dict(constraints["weight"])
            constraints["weight"] = X
            constraints.pop("alphabet",None)
            constraints.pop("min_order",None)
            constraints.pop("order",None)
            constraints.pop("max_order",None)
            constraints.pop("size",None)

        if "length" in constraints:
            constraints.pop("min_length",None)
            constraints.pop("max_length",None)
        min_k = constraints.get("min_length",0)
        max_k = constraints.get("max_length",infinity)
        assert min_k <= max_k, "min_length=%s <= max_length=%s"%(min_k, max_k)
        if min_k == max_k:
            constraints["length"] = \
                constraints.pop("min_length", constraints.pop("max_length"))

        if "order" in constraints:
           constraints.pop("min_order",None)
           constraints.pop("max_order",None)
        min_ord = constraints.get("min_order",0)
        max_ord = constraints.get("max_order",infinity)
        assert min_ord <= max_ord, "min_order=%s <= max_order=%s"%(min_ord, max_ord)
        if min_ord == max_ord:
            constraints["order"] = \
                constraints.pop("min_order", constraints.pop("max_order"))

        # pop keys with empty values, with the exception of 'size' or 'order'
        self.constraints = {}
        for (key,val) in constraints.iteritems():
            if val:
                self.constraints[key] = val
            elif key in ("size", "order", "length") and val is not None:
                self.constraints[key] = val

        self.full_constraints = dict(self.constraints)
        if hasattr(self, "_X"):
            self.full_constraints["weight"] = dict(self._X)
        if hasattr(self, "_n"):
            self.full_constraints["size"] = self._n
        if hasattr(self, "_alphabet"):
            self.full_constraints["alphabet"] = self._alphabet
            self.full_constraints["order"] = self._order

        if is_finite or _is_finite(constraints):
            Parent.__init__(self, category=FiniteEnumeratedSets())
        else:
            Parent.__init__(self, category=InfiniteEnumeratedSets())

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        return "Ordered Multiset Partitions"

    def _constraint_repr_(self, cdict=None):
        if not cdict:
            cdict = self.constraints
        constr = ""
        ss = ['%s=%s'%(key, val) for (key,val) in cdict.iteritems()]
        if len(ss) > 1:
            constr = " with constraints: " + ", ".join(ss)
        elif len(ss) == 1:
            constr = " with constraint: " + ", ".join(ss)
        return constr

    def _element_constructor_(self, lst):
        """
        Construct an element of ``self`` from ``lst``.

        EXAMPLES::

            sage: P = OrderedMultisetPartitions()
            sage: P([[3],[3,1]]) # indirect doctest
            [{3}, {1,3}]
            sage: P1 = OrderedMultisetPartitions(7, alphabet=3)
            sage: A1 = P1([[3],[3,1]]); A1
            [{3}, {1,3}]
            sage: P2 = OrderedMultisetPartitions(alphabet=3)
            sage: A2 = P2([[3],[3,1]]); A2
            [{3}, {1,3}]
            sage: A1 == A2
            True
            sage: P = OrderedMultisetPartitions(3)
            sage: P([[3],[3,1]])
            Traceback (most recent call last):
            ...
            AssertionError: cannot convert [[3], [3, 1]] into an element of
             Ordered Multiset Partitions of integer 3
        """
        ## construction for user shorthands
        if not lst:
            omp = []
        elif not isinstance(lst[0], (list, tuple, set, frozenset, Set_object)):
            omp = self.from_list(list(lst))

        ## construction for standard input
        else:
            omp = map(list, lst)

        if omp in self:
            return self.element_class(self, map(Set, omp))
        else:
            raise AssertionError("cannot convert %s into an element of %s"%(lst, self))

    Element = OrderedMultisetPartition

    def __contains__(self, x):
        """
        TESTS::

            sage: OMP = OrderedMultisetPartitions
            sage: [[2,1], [1,3]] in OMP()
            True
            sage: [[2,1], [1,3]] in OMP(7)
            True
            sage: [[2,2], [1,3]] in OMP()
            False
            sage: [] in OMP() and [] in OMP(0)
            True
            sage: [] in OMP(2)
            False
            sage: [[2, 1]] in OMP(3, length=2)
            False
            sage: [[2, -1]] in OMP()
            True
        """
        if not isinstance(x, (OrderedMultisetPartition, list, tuple)):
            return False
        else:
            return self._has_valid_blocks(x)

    def _has_valid_blocks(self, x):
        """
        Blocks should be nonempty sets/lists/tuples of distinct elements.
        """
        for block in x:
            if not isinstance(block, (list, tuple, set, Set_object)):
                return False
            if not tuple(block) or Set(block).cardinality() != len(tuple(block)):
                return False
        return True

    def _satisfies_constraints(self, x):
        X = _concatenate(x)
        co = OrderedMultisetPartitions(_get_weight(X))(x)
        def pass_test(co, (key,tst)):
            if key == 'size':
                return co.size() == tst
            if key == 'length':
                return co.length() == tst
            if key == 'min_length':
                return co.length() >= tst
            if key == 'max_length':
                return co.length() <= tst
            if key == 'weight':
                return co.weight() == dict(tst)
            if key == 'alphabet':
                if tst in ZZ:
                    tst = range(1,tst+1)
                return set(tst).issuperset(set(co.letters()))
            if key == 'order':
                return co.order() == tst
            if key == 'min_order':
                return co.order() >= tst
            if key == 'max_order':
                return co.order() <= tst
        return all(pass_test(co, (key,val)) for (key,val) in self.full_constraints.iteritems() if val)

    def from_list(self, lst):
        """
        Return an ordered multiset partition of singleton blocks, whose singletons
        are the elements ``lst``.

        INPUT:

        - ``lst`` -- an iterable

        EXAMPLES::

            sage: OrderedMultisetPartitions().from_list([1,4,8])
            [{1}, {4}, {8}]
            sage: OrderedMultisetPartitions().from_list('abaa')
            [{'a'}, {'b'}, {'a'}, {'a'}]
        """
        if all(a in ZZ for a in lst) and any(a < 0 for a in lst):
            raise ValueError("Something is wrong: `from_list` does not expect to see negative integers; received {}.".format(str(lst)))
        if 0 in list(lst) or '0' in list(lst):
            return self._from_zero_list(lst)
        else:
            d = [Set([x]) for x in lst]
            return self.element_class(self, d)

    def _from_zero_list(self, lst_with_zeros):
        r"""
        Return an ordered multiset partition from a list of nonnegative integers.
        Blocks are separated by zeros. Consecutive zeros are ignored.

        EXAMPLES::

            sage: OrderedMultisetPartitions().from_list([1,2,4])
            [{1}, {2}, {4}]
            sage: OrderedMultisetPartitions()._from_zero_list([1,2,4])
            [{1,2,4}]
            sage: OrderedMultisetPartitions()._from_zero_list([1,0,2,0,0,4])
            [{1}, {2}, {4}]
            sage: OrderedMultisetPartitions()._from_zero_list('abc00a0b')
            [{'a','b','c'}, {'a'}, {'b'}]
        """
        from_zero_lst = list(lst_with_zeros)
        if from_zero_lst[-1] not in {0,'0'}:
            from_zero_lst += [0]
        co = []; block=[]
        for a in from_zero_lst:
            if a in {0,'0'}:
                if block:
                    co.append(block)
                    block = []
            else:
                block.append(a)
        if self._has_valid_blocks(co):
            return self.element_class(self, map(Set, co))
        else:
            raise ValueError("ordered multiset partitions do not have repeated entries within blocks (%s received)"%str(co))

    def an_element(self):
        """
        Return an element of ``self``.

        Rudimentary. Picks the first valid element served up by ``self.__iter__()``.
        """
        try:
            iteration = self.__iter__()
            while True:
                co = next(iteration)
                if co in self:
                    return co
        except StopIteration:
            raise EmptySetError("%s is the empty set"%self)

    def __iter__(self):
        """
        Iterate over ordered multiset partitions.

        EXAMPLES::

            sage: OrderedMultisetPartitions(3).list()
            [[{3}], [{1,2}], [{2}, {1}], [{1}, {2}], [{1}, {1}, {1}]]
            sage: OrderedMultisetPartitions(0).list()
            [[]]
            sage: C = OrderedMultisetPartitions()
            sage: it = C.__iter__()
            sage: [next(it) for i in range(16)]
            [[], [{1}], [{2}], [{1}, {1}], [{3}], [{1,2}], [{2}, {1}],
             [{1}, {2}], [{1}, {1}, {1}], [{4}], [{1,3}], [{3}, {1}],
             [{1,2}, {1}], [{2}, {2}], [{2}, {1}, {1}], [{1}, {3}]]

        TESTS::

            sage: OrderedMultisetPartitions(alphabet=[1,3], max_length=2).list()
            [[], [{1}], [{3}], [{1,3}], [{1}, {1}], [{1}, {3}],
             [{3}, {1}], [{3}, {3}], [{1,3}, {1}], [{1,3}, {3}],
             [{1}, {1,3}], [{3}, {1,3}], [{1,3}, {1,3}]]
            sage: C = OrderedMultisetPartitions(min_length=2, max_order=2)
            sage: it = C.__iter__()
            sage: [next(it) for i in range(15)]
            [[{1}, {1}], [{2}, {1}], [{1}, {2}], [{3}, {1}], [{2}, {2}],
             [{1}, {3}], [{4}, {1}], [{3}, {2}], [{2}, {3}], [{1}, {4}],
             [{5}, {1}], [{4}, {2}], [{3}, {3}], [{2}, {4}], [{1}, {5}]]
            sage: OrderedMultisetPartitions(alphabet=[1,3], min_length=2).list()
            Traceback (most recent call last):
            ...
            NotImplementedError: cannot list an infinite set
        """
        iterator = _base_iterator(self.full_constraints)
        if iterator:
            for co in iterator:
                if self._satisfies_constraints(co):
                    yield self.element_class(self, co)
        else:
            # iterate over partitions of multisets of positive integers
            # or over letters over an alphabet
            if "alphabet" in self.constraints:
                A = self.constraints["alphabet"]
                # establish a cutoff order `max_ell`
                max = self.constraints.get("max_length", infinity)
                max = self.constraints.get("length", max)
                max = max * len(A)
                max = self.constraints.get("max_order", max)
                max_ell = self.constraints.get("order", max)
                ell = 0
                while True and ell <= max_ell:
                    for co in _iterator_order(A, ell):
                        if self._satisfies_constraints(co):
                            yield self.element_class(self, co)
                    ell += 1
            else:
                n = 0
                while True:
                    for co in _iterator_size(n):
                        if self._satisfies_constraints(co):
                            yield self.element_class(self, co)
                    n += 1

###############

class OrderedMultisetPartitions_all_constraints(OrderedMultisetPartitions):
    """
    Class of all ordered multiset partitions (with or without constraints).

    EXAMPLES::

        sage: C = OrderedMultisetPartitions(); C
        Ordered Multiset Partitions
        sage: [[1],[1,'a']] in C
        True

        sage: OrderedMultisetPartitions(weight=[2,0,1], length=2)
        Ordered Multiset Partitions with constraints: length=2, weight={1: 2, 3: 1}
    """
    def __init__(self, **constraints):
        """
        Initialize ``self``.

        TESTS::

            sage: C = OrderedMultisetPartitions()
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()

            sage: C = OrderedMultisetPartitions(weight=[2,0,1], length=2)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()

            sage: D1 = OrderedMultisetPartitions(weight={1:2, 3:1}, min_length=2, max_length=2)
            sage: D2 = OrderedMultisetPartitions({1:2, 3:1}, min_length=2, max_length=2)
            sage: D3 = OrderedMultisetPartitions(5, weight={1:2, 3:1}, length=2)
            sage: D4 = OrderedMultisetPartitions([1,3], 3, weight={1:2, 3:1}, length=2)
            sage: D5 = OrderedMultisetPartitions([1,3], 3, size=5, length=2)
            sage: any(C == eval('D'+str(i)) for i in range(1,6))
            False
            sage: all(Set(C) == Set(eval('D'+str(i))) for i in range(1,6))
            True
            sage: E = OrderedMultisetPartitions({1:2, 3:1}, size=5, min_length=2)
            sage: Set(C) == Set(E)
            False
        """
        OrderedMultisetPartitions.__init__(self, None, **constraints)

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        return "Ordered Multiset Partitions" + self._constraint_repr_()

    def subset(self, *args):
        """
        Return a subset of all ordered multiset partitions `c`.

        Expects one or two arguments, with different subsets resulting:

        - One Argument:

          * ``X`` -- a dictionary (representing a multiset for `c`),
            or an integer (representing the size of `c`)

        - Two Arguments:

          * ``alph`` -- a list (representing allowable letters within `c`),
            or a positive integer (representing the maximal allowable letter)
          * ``ord``  -- a nonnegative integer (the total number of letters
            within `c`)

        EXAMPLES::

            sage: C = OrderedMultisetPartitions()
            sage: C.subset(3)
            Ordered Multiset Partitions of integer 3
            sage: C.subset(3) == OrderedMultisetPartitions(3)
            True
            sage: C.subset([1,1,4])
            Ordered Multiset Partitions of multiset {{1, 1, 4}}
            sage: C.subset([1,4], 2)
            Ordered Multiset Partitions of order 2 over alphabet {1, 4}
        """
        if not args:
            return self
        return OrderedMultisetPartitions(*args, **self.constraints)

###############

class OrderedMultisetPartitions_n(OrderedMultisetPartitions):
    """
    Class of ordered multiset partitions of a fixed integer `n`.
    """
    def __init__(self, n):
        """

        TESTS::

            sage: C = OrderedMultisetPartitions(Integer(4))
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
            sage: C2 = OrderedMultisetPartitions(int(4))
            sage: C is C2
            True
            sage: C3 = OrderedMultisetPartitions(7/2)
            Traceback (most recent call last):
            ...
            ValueError:  7/2 must be a nonnegative integer or a list or
             dictionary representing a multiset
        """
        self._n = n
        OrderedMultisetPartitions.__init__(self, True)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        TESTS::

            sage: repr(OrderedMultisetPartitions(3))
            'Ordered Multiset Partitions of integer 3'
        """
        return "Ordered Multiset Partitions of integer %s" % self._n

    def _has_valid_blocks(self, x):
        """
        Check that blocks of ``x`` are valid.

        Blocks should be nonempty sets/lists/tuples of distinct positive
        integers. Also the sum of all integers should be ``self._n``.
        """
        no_repeats = OrderedMultisetPartitions._has_valid_blocks(self, x)
        nonnegative = all((i in ZZ and i > 0) for block in x for i in block)
        valid_sum = sum(map(sum, x)) == self._n
        return no_repeats and nonnegative and valid_sum

    def cardinality(self):
        """
        Return the number of ordered multiset partitions of integer ``self._n``.
        """
        # Dispense with the complex computation for small orders.
        orders = {0:1, 1:1, 2:2, 3:5, 4:11, 5:25}
        if self._n <= 5:
            return ZZ(orders[self._n])

        # We view an ordered multiset partition as a list of 2-regular integer partitions.
        #
        # The 2-regular partitions have a nice generating function (see OEIS:A000009).
        # Below, we take (products of) coefficients of polynomials to compute cardinality.
        t = var('t')
        partspoly = prod([1+t**k for k in range(1,self._n+1)]).coefficients()
        def partspoly_coeff(d): return partspoly[d][0]
        deg = 0
        for alpha in Compositions(self._n):
            deg += prod([partspoly_coeff(d) for d in alpha])
        return ZZ(deg)

    def an_element(self):
        """
        Return a typical element of ``OrderedMultisetPartition_n``.
        """
        #output will have at most three blocks, each of size 1, 2, or 3.
        alpha = Compositions(self._n, max_part=self._n//3+1).an_element()
        out = []
        for a in alpha:
            if a in {1, 2, 4}:
                out.append([a])
            else:
                if a % 2:
                    out.append([a//2+1, a//2])
                else:
                    out.append([a//2, a//2-1, 1])
        return self.element_class(self, map(Set, out))

    def random_element(self):
        """
        Return a random ``OrderedMultisetPartition_n`` with uniform probability.

        .. TODO::

            Is it really uniform probability?

        This method generates a random composition and then
        then creates new blocks after positions that are not ascents.

        EXAMPLES::

            sage: OrderedMultisetPartitions(5).random_element() # random
            [{1,2}, {1}, {1}]
            sage: OrderedMultisetPartitions(5).random_element() # random
            [{2}, {1,2}]
        """
        C = Compositions(self._n).random_element()
        co = _break_at_descents(C)
        return self.element_class(self, map(Set, co))

    def __iter__(self):
        return _iterator_size(self._n)

class OrderedMultisetPartitions_n_constraints(OrderedMultisetPartitions):
    """
    Class of ordered multiset partitions of a fixed integer `n` satisfying constraints.
    """
    def __init__(self, n, **constraints):
        """
        Mimic class ``OrderedMultisetPartitions_n`` to initialize.

        TESTS::

            sage: C = OrderedMultisetPartitions(6, length=3)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()

            sage: C = OrderedMultisetPartitions(6, weight=[3,0,1], length=3)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
        """
        self._n = n
        OrderedMultisetPartitions.__init__(self, True, size=n, **constraints)

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        cdict = dict(self.constraints)
        cdict.pop("size", None)
        base_repr = "Ordered Multiset Partitions of integer %s" % self._n
        return base_repr + self._constraint_repr_(cdict)

    def _has_valid_blocks(self, x):
        """
        Check that blocks of ``x`` are valid and satisfy constraints.
        """
        valid = OrderedMultisetPartitions_n(self._n)._has_valid_blocks(x)
        return valid and self._satisfies_constraints(x)

###############

class OrderedMultisetPartitions_X(OrderedMultisetPartitions):
    """
    Class of ordered multiset partitions of a fixed multiset `X`.
    """
    def __init__(self, X):
        """
        TESTS::

            sage: C = OrderedMultisetPartitions([1,1,4])
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
            sage: C2 = OrderedMultisetPartitions({1:2, 4:1})
            sage: C is C2
            True
        """
        self._X = X
        self._Xtup = tuple([k for (k,v) in sorted(X) for _ in range(v)])
        OrderedMultisetPartitions.__init__(self, True)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        TESTS::

            sage: repr(OrderedMultisetPartitions([1,1,4]))
            'Ordered Multiset Partitions of multiset {{1, 1, 4}}'
        """
        ms_rep = "{{" + ", ".join(map(str, self._Xtup)) + "}}"
        return "Ordered Multiset Partitions" + " of multiset %s"%ms_rep

    def _has_valid_blocks(self, x):
        """
        Check that blocks of ``x`` are valid.

        Blocks should be nonempty sets/lists/tuples whose union is the given multiset.
        """
        no_repeats = OrderedMultisetPartitions._has_valid_blocks(self, x)
        valid_partition = _get_multiset(x) == self._Xtup
        return no_repeats and valid_partition

    def cardinality(self):
        """
        Return the number of ordered partitions of multiset ``X``.
        """
        if self._Xtup == ():
            return ZZ(0)

        # We build ordered multiset partitions of `X` by permutation + deconcatenation
        # Is there a balls-and-boxes formula for this?

        deg = 0
        for alpha in Permutations_mset(self._Xtup):
            fattest = _break_at_descents(alpha)
            deg += prod(2**(len(k)-1) for k in fattest)
        return ZZ(deg)

    def an_element(self):
        """
        Return a typical ``OrderedMultisetPartition_X``.
        """
        if not self._Xtup:
            return self.element_class(self, [])
        alpha = Permutations_mset(self._Xtup).an_element()
        co = _break_at_descents(alpha)

        # construct "an element" by breaking the first fat block of `co` in two
        elt = []
        for i in range(len(co)):
            if len(co[i])==1:
                elt.append(co[i])
            else:
                break
        elt.append(co[i][:len(co[i])//2 + 1])
        elt.append(co[i][len(co[i])//2 + 1:])
        elt.extend(co[i+1:])
        return self.element_class(self, map(Set, elt))

    def random_element(self):
        """
        Return a random ``OrderedMultisetPartition`` with uniform probability.

        .. TODO::

            Is it really uniform probability?

        This method:

        - generates a random permutation of the multiset, then
        - creates new blocks after positions that are not ascents to
          build ``fat``, then
        - takes a random element of ``fat.finer()``.

        EXAMPLES::

            sage: OrderedMultisetPartitions([1,1,3]).random_element() # random
            [{1}, {1,3}]
            sage: OrderedMultisetPartitions([1,1,3]).random_element() # random
            [{3}, {1}, {1}]
        """
        if not self._Xtup:
            return self.element_class(self, [])

        alpha = Permutations_mset(self._Xtup).random_element()
        co = _break_at_descents(alpha)
        finer = self.element_class(self, map(Set,co)).finer()
        return finer.random_element()

    def __iter__(self):
        return _iterator_weight(weight=dict(self._X))

class OrderedMultisetPartitions_X_constraints(OrderedMultisetPartitions):
    """
    Class of ordered multiset partitions of a fixed multiset `X`
    satisfying constraints.
    """
    def __init__(self, X, **constraints):
        """
        Mimic class ``OrderedMultisetPartitions_X`` to initialize.

        TESTS::

            sage: C = OrderedMultisetPartitions([1,1,2,4], length=3)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()

            sage: C = OrderedMultisetPartitions([1,1,2,4], weight=[3,0,1], max_length=3) # weight ignored
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
        """
        self._X = X
        self._Xtup = tuple(k for (k,v) in sorted(X) for _ in range(v))
        OrderedMultisetPartitions.__init__(self, True, **constraints)

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        cdict = dict(self.constraints)
        cdict.pop("weight", None)
        ms_rep = "{{" + ", ".join(map(str, self._Xtup)) + "}}"
        base_repr = "Ordered Multiset Partitions" + " of multiset %s"%ms_rep
        return base_repr + self._constraint_repr_(cdict)

    def _has_valid_blocks(self, x):
        """
        Check that blocks of ``x`` are valid and satisfy constraints.
        """
        valid = OrderedMultisetPartitions_X(self._X)._has_valid_blocks(x)
        return valid and self._satisfies_constraints(x)

###############

class OrderedMultisetPartitions_A(OrderedMultisetPartitions):
    """
    Class of ordered multiset partitions of specified order `d`
    over a fixed alphabet `A`.
    """
    def __init__(self, A, d):
        """
        TESTS::

            sage: C = OrderedMultisetPartitions(3, 2)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
            sage: C2 = OrderedMultisetPartitions([1,2,3], 2)
            sage: C is C2
            True
            sage: list(OrderedMultisetPartitions([1,2,3], 2))
            [[{1,2}], [{1,3}], [{2,3}], [{1}, {1}], [{1}, {2}], [{1}, {3}], [{2}, {1}],
             [{2}, {2}], [{2}, {3}], [{3}, {1}], [{3}, {2}], [{3}, {3}]]
        """
        self._alphabet = A
        self._order = d
        OrderedMultisetPartitions.__init__(self, True)

    def _repr_(self):
        """
        Return a string representation of ``self``.

        TESTS::

            sage: repr(OrderedMultisetPartitions(3, 2))
            'Ordered Multiset Partitions of order 2 over alphabet {1, 2, 3}'
            sage: repr(OrderedMultisetPartitions([1,3], 2))
            'Ordered Multiset Partitions of order 2 over alphabet {1, 3}'
        """
        A_rep = "Ordered Multiset Partitions of order " + str(self._order)
        A_rep += " over alphabet {%s}"%(", ".join(map(str, sorted(self._alphabet))))
        return A_rep

    def _has_valid_blocks(self, x):
        """
        Check that blocks of ``x`` are valid.

        Blocks should be nonempty sets/lists/tuples of order ``self._order``
        all of whose elements are taken from ``self._alphabet``.
        """
        no_repeats = OrderedMultisetPartitions._has_valid_blocks(self, x)
        valid_order = sum([len(tuple(block)) for block in x]) == self._order
        valid_letters = self._alphabet.issuperset(Set(_concatenate(x)))
        return no_repeats and valid_order and valid_letters

    def an_element(self):
        """
        Return a typical ``OrderedMultisetPartition_A``.
        """
        alpha = Compositions(self._order).an_element()
        co = [Subsets_sk(self._alphabet, a).an_element() for a in alpha]
        return self.element_class(self, map(Set, co))

    def random_element(self):
        """
        Return a random ``OrderedMultisetPartition_A`` with uniform probability.

        .. TODO::

            Is it really uniform probability?

        This method:

        - generates a random permutation of the multiset, then
        - creates new blocks after positions that are not ascents
          to build ``fat``, then
        - takes a random element of ``fat.finer()``.

        EXAMPLES::

            sage: OrderedMultisetPartitions([1,4], 3).random_element() # random
            [{4}, {1,4}]
            sage: OrderedMultisetPartitions([1,3], 4).random_element() # random
            [{1,3}, {1}, {3}]
        """
        if not self._alphabet:
            return self.element_class(self, [])

        alpha = Compositions(self._order, max_part=len(self._alphabet)).random_element()
        co = [Subsets_sk(self._alphabet, a).random_element() for a in alpha]
        return self.element_class(self, map(Set, co))

    def __iter__(self):
        return _iterator_order(self._alphabet, self._order)

    def cardinality(self):
        """
        Return the number of ordered partitions of order ``self._order`` on
        alphabet ``self._alphabet``.

        TESTS::

            sage: len(OrderedMultisetPartitions([0,42], 3).list())
            12
        """
        if self._order == 0:
            return ZZ(0)

        # iteration scheme:
        # - start from an integer composition ``alpha`` of ``self._order``.
        # - for each ``a`` in ``alpha``, pick ``a`` letters from ``alphabet``
        min_length = self._order // len(self._alphabet)
        max_length = self._order

        deg = 0
        for k in range(min_length, max_length+1):
            for alpha in Compositions(self._order, length=k, max_part=len(self._alphabet)):
                deg += prod(binomial(len(self._alphabet), a) for a in alpha)
        return ZZ(deg)

class OrderedMultisetPartitions_A_constraints(OrderedMultisetPartitions):
    """
    Class of ordered multiset partitions of specified order `d`
    over a fixed alphabet `A` satisfying constraints.
    """
    def __init__(self, A, d, **constraints):
        """
        Mimic class ``OrderedMultisetPartitions_A`` to initialize.

        EXAMPLES::

            sage: list(OrderedMultisetPartitions(3, 2, length=3)) # should be empty
            []
            sage: list(OrderedMultisetPartitions([1,2,4], 2, length=1))
            [[{1,2}], [{1,4}], [{2,4}]]

        TESTS::

            sage: C = OrderedMultisetPartitions(3, 2, length=3)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
            sage: C = OrderedMultisetPartitions([1,2,4], 4, min_length=3)
            sage: C == loads(dumps(C))
            True
            sage: TestSuite(C).run()
        """
        self._alphabet = A
        self._order = d
        OrderedMultisetPartitions.__init__(self, True, **constraints)

    def _repr_(self):
        """
        Return a string representation of ``self``.
        """
        cdict = dict(self.constraints)
        cdict.pop("alphabet", None)
        cdict.pop("order", None)
        base_repr = "Ordered Multiset Partitions of order " + str(self._order)
        base_repr += " over alphabet {%s}"%(", ".join(map(str, sorted(self._alphabet))))
        return base_repr + self._constraint_repr_(cdict)

    def _has_valid_blocks(self, x):
        """
        Check that blocks of ``x`` are valid and satisfy constraints.
        """
        valid = OrderedMultisetPartitions_A(self._alphabet, self._order)._has_valid_blocks(x)
        return valid and self._satisfies_constraints(x)

    def an_element(self):
        """
        Return a typical ``OrderedMultisetPartition_A``.
        """
        keys = self.constraints.keys()
        n = len(self._alphabet)
        ell = self._order
        if list(keys) == ["length"]:
            kmin = kmax = k = self.constraints["length"]
            if (ell < kmin) or (n * kmax < ell):
                raise EmptySetError("%s is the empty set"%self)
            alpha = Compositions(ell, length=k, max_part=n).an_element()
            co = [Subsets_sk(self._alphabet, a).an_element() for a in alpha]
            #assume ``co`` satisfies all constraints
            return self.element_class(self, map(Set, co))
        else:
            try:
                return next(self.__iter__())
            except StopIteration:
                raise EmptySetError("%s is the empty set"%self)

###############

def _get_multiset(co):
    """
    Construct the multiset (as a sorted tuple) suggested by the lists of lists ``co``.
    """
    return tuple(sorted(_concatenate(co)))

def _get_weight(lst):
    """
    Construct the multiset (as a dictionary) suggested by the multiset-as-list ``lst``.
    """
    out = {}
    for k in lst:
        out[k] = out.get(k,0) + 1
    return out

def _union_of_sets(list_of_sets):
    """
    Return the union of a list of iterables as a Set object.
    """
    return reduce(lambda a,b: Set(a)|Set(b), list_of_sets, Set([]))

def _concatenate(list_of_iters):
    """
    Return the concatenation of a list of iterables as a tuple.
    """
    #if not list_of_iters:
    #    return []
    #return reduce(lambda a,b: a+b, list_of_iters)
    return tuple(_ for block in list_of_iters for _ in block)

def _is_finite(constraints):
    """
    Return ``True`` if the dictionary ``constraints`` corresponds to
    a finite collection of ordered multiset partitions.
    """
    if "weight" in constraints or "size" in constraints:
        return True
    elif "alphabet" in constraints:
        Bounds = Set(["length", "max_length", "order", "max_order"])
        return Bounds.intersection(Set(constraints)) != Set()

def _base_iterator(constraints):
    """
    Return a base iterator for ordered multiset partitions or ``None``.

    If the keys within ``constraints`` dictionary correspond to a finite set
    of ordered multiset partitions, return an iterator. Else, return ``None``.
    """
    if "weight" in constraints:
        return _iterator_weight(constraints["weight"])
    elif "size" in constraints:
        return _iterator_size(constraints["size"], \
            constraints.get("length",None), constraints.get("alphabet",None))
    elif "alphabet" in constraints:
        A = constraints["alphabet"]
        # assumes `alphabet` is finite
        min_k = constraints.get("min_length", 0)
        max_k = constraints.get("max_length", infinity)
        min_ord = constraints.get("min_order", 0)
        max_ord = constraints.get("max_order", infinity)
        max_k = min(max_k, max_ord)
        if "length" in constraints:
            min_k = max_k = constraints["length"]
            min_ord = max(min_ord, min_k)
            max_ord = min(max_ord, len(A) * max_k)
        if "order" in constraints:
            min_ord = max_ord = constraints["order"]
            max_k = min(max_k, max_ord)
            if min_ord:
                min_k =max(1, min_k, min_ord // len(A))
        if infinity not in (max_k, max_ord):
            return chain(*(_iterator_order(A, ord, range(min_k, max_k+1)) \
                        for ord in range(min_ord, max_ord+1)))
    # else
    return None

def _iterator_weight(weight):
    """
    An iterator for the ordered multiset partitions with weight given by
    the dictionary (or weak composition) ``weight``.

    EXAMPLES::

        sage: from sage.combinat.multiset_partition_ordered import _iterator_weight
        sage: list(_iterator_weight({'a':2, 'b':1}))
        [[{'a'}, {'a'}, {'b'}], [{'a'}, {'a','b'}], [{'a'}, {'b'}, {'a'}],
         [{'a','b'}, {'a'}], [{'b'}, {'a'}, {'a'}]]
        sage: list(_iterator_weight([3,0,1]))
        [[{1}, {1}, {1}, {3}], [{1}, {1}, {1,3}], [{1}, {1}, {3}, {1}],
         [{1}, {1,3}, {1}], [{1}, {3}, {1}, {1}],
         [{1,3}, {1}, {1}], [{3}, {1}, {1}, {1}]]
    """
    if isinstance(weight, (list, tuple)):
        weight = {k+1: val for k,val in enumerate(weight) if val > 0}
    if isinstance(weight, dict):
        multiset = tuple([k for k in sorted(weight) for _ in range(weight[k])])
    P = OrderedMultisetPartitions_X(tuple(weight.iteritems()))

    if not multiset:
        yield P([])
    else:
        # We build ordered multiset partitions of `X` by permutation + deconcatenation
        for alpha in Permutations_mset(multiset):
            co = _break_at_descents(alpha, weak=True)
            for A in P(co).finer(strong=True):
                yield A


def _iterator_size(size, length=None, alphabet=None):
    r"""
    An iterator for the ordered multiset partitions of integer `n`.

    The degree `n` part of ordered multiset partition contains all sequences of
    subsets of `\NN_+` whose total sum adds up to `n`.

    If optional argument ``alphabet`` is given, it should be a ``Set`` object.
    Then only yield those `c` with all letters taken from ``alphabet``

    TESTS::

        sage: from sage.combinat.multiset_partition_ordered import _iterator_size
        sage: list(_iterator_size(3))
        [[{3}], [{1,2}], [{2}, {1}], [{1}, {2}], [{1}, {1}, {1}]]
        sage: list(_iterator_size(5, alphabet={1,3}))
        [[{1,3}, {1}], [{3}, {1}, {1}], [{1}, {1,3}], [{1}, {3}, {1}],
         [{1}, {1}, {3}], [{1}, {1}, {1}, {1}, {1}]]
    """
    # iteration scheme:
    # - start from an integer composition ``alpha``.
    # - for each ``a`` in ``alpha``, pick distinct integers that sum to ``a``
    P = OrderedMultisetPartitions_n(size)
    if alphabet:
        min_p = min(alphabet)
        max_p = max(alphabet)
        for alpha in Compositions(size, length=length):
            for p in cartesian_product([IntegerListsLex(a, min_slope=1, \
                    min_part=min_p, max_part=min(a, max_p)) for a in alpha]):
                if Set(_concatenate(p)).issubset(Set(alphabet)):
                    yield P([Set(list(k)) for k in p])
    else:
        for alpha in Compositions(size, length=length):
            for p in cartesian_product([IntegerListsLex(a, min_slope=1, \
                    min_part=1) for a in alpha]):
                yield P([Set(list(k)) for k in p])

def _iterator_order(A, d, lengths=None):
    """
    An iterator for the ordered multiset partitions of order `d` over alphabet `A`.

    If optional argument ``lengths`` is given, it should be a list of integers.
    Then only yield ordered multiset partitions with length in ``lengths``.

    TESTS::

        sage: from sage.combinat.multiset_partition_ordered import _iterator_order
        sage: list(_iterator_order({1,4}, 3))
        [[{1,4}, {1}], [{1,4}, {4}], [{1}, {1,4}], [{4}, {1,4}], [{1}, {1}, {1}],
         [{1}, {1}, {4}], [{1}, {4}, {1}], [{1}, {4}, {4}], [{4}, {1}, {1}],
         [{4}, {1}, {4}], [{4}, {4}, {1}], [{4}, {4}, {4}]]
        sage: list(_iterator_order([1,4], 3, [3]))
        [[{1}, {1}, {1}], [{1}, {1}, {4}], [{1}, {4}, {1}], [{1}, {4}, {4}],
         [{4}, {1}, {1}], [{4}, {1}, {4}], [{4}, {4}, {1}], [{4}, {4}, {4}]]
        sage: list(_iterator_order([1,2,4], 3, [1,2]))[:10]
        [[{1,2,4}],  [{1,2}, {1}], [{1,2}, {2}], [{1,2}, {4}], [{1,4}, {1}],
         [{1,4}, {2}], [{1,4}, {4}], [{2,4}, {1}], [{2,4}, {2}], [{2,4}, {4}]]
        sage: list(_iterator_order([1,4], 3, [4]))
        []
        sage: list(_iterator_order([1,4], 0, [3]))
        []
        sage: list(_iterator_order([1,4], 0, [0,3]))
        [[]]
        sage: list(_iterator_order([1,4], 0))
        [[]]
    """
    A = Set(A)
    P = OrderedMultisetPartitions_A(A, d)

    # iteration scheme:
    # start from an integer composition ``alpha`` of ``d``.
    # for each ``a`` in ``alpha``, pick ``a`` letters from ``A``
    n = len(A)
    if not lengths:
        if d:
            lengths = range(max(1, d // n), d+1)
        else:
            lengths = (0,)

    for k in lengths:
        if not k and not d:
            yield P([])
        else:
            for alpha in Compositions(d, length=k, max_part=n):
                for co in cartesian_product([Subsets_sk(A, a) for a in alpha]):
                    yield P(co)

def _partial_sum(lst):
    """
    Return partial sums of elements in ``lst``.

    EXAMPLES::

        sage: from sage.combinat.multiset_partition_ordered import _partial_sum
        sage: lst = [1,3,5]
        sage: _partial_sum(lst)
        [0, 1, 4, 9]
    """
    result = [0]
    for i in range(len(lst)):
        result.append(result[-1]+lst[i])
    return result

def _descents(w):
    r"""
    Return descent positions in the word ``w``.
    """
    return [j for j in range(len(w)-1) if w[j] > w[j+1]]

def _break_at_descents(alpha, weak=True):
    if not alpha:
        return []

    Blocks = []
    block = [alpha[0]]
    for i in range(1,len(alpha)):
        if (alpha[i-1] > alpha[i]) or (alpha[i-1] == alpha[i] and weak):
            Blocks.append(block)
            block = [alpha[i]]
        else:
            block.append(alpha[i])
    if block:
        Blocks.append(block)
    return Blocks

def _refine_block(S, strong=False):
    r"""
    Return the set of all possible refinements of a set `S`.

    A refinement of `S` is a tuple of nonempty subsets whose union is `S`.

    If optional argument ``strong`` is set to ``True``, then only those
    refinements that are deconcatenations of the list ``sorted(S)`` are returned.
    """
    X = list(S)
    n = len(X)
    out = []
    if not strong:
        WordSet = IntegerListsLex(min_part=0, max_part=n-1, length=n)
    else:
        WordSet = IntegerListsLex(min_part=0, max_part=n-1, length=n, min_slope=0)

    for w in WordSet:
        if _is_initial_segment(sorted(set(w))):
            a = [set([]) for _ in range(max(w)+1)]
            for pos in range(n):
                a[w[pos]].add(X[pos])
            out.append(a)
    return Set([tuple(map(Set,x)) for x in out])

def _is_initial_segment(lst):
    r"""
    Return True if ``lst`` is an interval in `\ZZ` of the form `[0, 1, \ldots, n]`.
    """
    return list(range(max(lst)+1)) == lst

def _split_block(S, k=2):
    """
    Return the set of all possible splittings of a set `S` into `k` parts.

    A splitting of `S` is a tuple of (possibly empty) subsets whose union is `S`.
    """
    X = list(S)
    n = len(X)
    out = []
    WordSet = IntegerListsLex(min_part=0, max_part=k-1, length=n)
    for w in WordSet:
        a = [set([]) for _ in range(k)]
        for pos in range(n):
            a[w[pos]].add(X[pos])
        out.append(a)
    return Set([tuple(map(Set,x)) for x in out])

def _to_minimaj_blocks(T):
    r"""
    Return a tuple of tuples, representing a ordered multiset partition in
    the minimaj ordering on blocks

    Input: a sequence ``T`` of row words corresponding to (skew-)tableaux.

    Output: the minimaj bijection `\varphi^{-1}` of [BCHOPSY2017]_ applied to ``T``.

    EXAMPLES::

        sage: from sage.combinat.multiset_partition_ordered import _to_minimaj_blocks
        sage: co = OrderedMultisetPartitions(14).an_element(); co
        [{2,3}, {2,3}, {4}]
        sage: co.to_tableau()
        [[3, 2], [], [3, 2, 4]]
        sage: _to_minimaj_blocks(co.to_tableau()) == co.minimaj_blocks()
        True
    """
    mu = [(i,) for i in T[-1]]
    breaks = [0] + _descents(T[-1]) + [len(mu)-1]
    T = [T[i][::-1] for i in range(len(T)-1)][::-1]
    for f in range(len(breaks)-1):
        for j in range(breaks[f],breaks[f+1]+1):
            mu[j] += tuple(i for i in T[f] if (mu[j][0] < i or j == breaks[f])
                                               and (j == breaks[f+1] or i <= mu[j+1][0]))
    return tuple(mu)


###############

class MinimajCrystal(UniqueRepresentation, Parent):
    r"""
    Crystal of ordered multiset partitions with `ell` letters from alphabet
    `\{1,2,...,n\}` divided into `k` blocks.

    Elements are represented in the minimaj ordering of blocks as in Benkart, et al.

    .. NOTES:

    - Elements are not stored internally as ordered multiset partitions, but as words
      according to the minimaj bijection `\varphi` of Benkart, et al.

    - Initial draft of code provided by Anne Schilling.

    REFERENCES:

    - [BCHOPSY2017]_

    EXAMPLES::

        sage: list(crystals.Minimaj(2,3,2))
        [((2, 1), (1,)), ((2,), (1, 2)), ((1,), (1, 2)), ((1, 2), (2,))]

        sage: b = crystals.Minimaj(3, 5, 2).an_element(); b
        ((2, 3, 1), (1, 3))
        sage: b.e(2)
        ((2, 3, 1), (1, 2))
    """
    def __init__(self, n, ell, k):
        """
        Initialize ``self``.

        TESTS::

            sage: B = crystals.Minimaj(2,3,2)
            sage: B == loads(dumps(B))
            True
            sage: B = crystals.Minimaj(3, 5, 2)
            sage: TestSuite(B).run()

            sage: list(crystals.Minimaj(4,2,3)) # more blocks than letters
            []
            sage: list(crystals.Minimaj(2,6,3))
            [((1, 2), (2, 1), (1, 2))]
            sage: list(crystals.Minimaj(2,5,2)) # blocks too fat for alphabet
            []
        """
        Parent.__init__(self, category=ClassicalCrystals())
        self.n = n
        self.k = k
        self.ell = ell
        self._cartan_type = CartanType(['A',n-1])
        B = Letters(['A', n-1])
        T = tensor([B]*ell)
        self._BT = (B, T)
        self._OMPs = OrderedMultisetPartitions(n, ell, length=k)
        self.module_generators = []
        for co in self._OMPs:
            t = co.to_tableau()
            word = T(*[B(a) for a in _concatenate(t)])
            blocks = [len(h) for h in t]
            breaks = tuple(_partial_sum(blocks))
            mu = self.element_class(self, (word, breaks))
            self.module_generators.append(mu)

    def _repr_(self):
        """
        Return the string representation of ``self``.

        EXAMPLES::

            sage: B = crystals.Minimaj(3,4,2); B
            Minimaj Crystal of type A_2 of words of length 4 into 2 blocks
        """
        return "Minimaj Crystal of type A_%s of words of length %s into %s blocks"%(self.n-1, self.ell, self.k)

    def an_element(self):
        """
        Return a typical element of ``self``.
        """
        t = self._OMPs.an_element().to_tableau()
        breaks = tuple(_partial_sum([len(h) for h in t]))
        B,T = self._BT
        return self.element_class(self, (T(*[B(a) for a in _concatenate(t)]), breaks))

    def _element_constructor_(self, x):
        """
        Build an element of Minimaj from the ordered multiset partition ``x``.
        """
        # trap for case x is already an element of Minimaj.
        if hasattr(x, "value"):
            return self.element_class(self, x)
        else:
            # Assume ``x`` is an ordered multiset partition.
            t = self._OMPs(x).to_tableau()
            breaks = tuple(_partial_sum([len(h) for h in t]))
            B,T = self._BT
            return self.element_class(self, (T(*[B(a) for a in _concatenate(t)]), breaks))

    def __contains__(self, x):
        """
        Return ``True`` if ``x`` is an element of ``self`` or an ordered multiset partition.
        """
        if hasattr(x,"parent"):
            return x.parent() == self
        else:
            return x in self._OMPs

    def from_tableau(self, t):
        r"""
        Return the bijection `\varphi^{-1}` of [BCHOPSY2017]_ applied to ``t``.

        EXAMPLES::

            sage: B = crystals.Minimaj(3,6,3)
            sage: b = B.an_element(); b
            ((1, 2, 3), (3, 1), (2,))
            sage: t = b.to_tableau(); t
            [[1], [3, 2], [1, 3, 2]]

        TESTS::

            sage: B = crystals.Minimaj(3,6,3)
            sage: all(mu == B.from_tableau(mu.to_tableau()) for mu in B)
            True
            sage: t = B.an_element().to_tableau()
            sage: B1 = crystals.Minimaj(3,6,2)
            sage: B1.from_tableau(t)
            Traceback (most recent call last):
            ...
            AssertionError: ((1, 2, 3), (3, 1), (2,)) is not an element of
             Minimaj Crystal of type A_2 of words of length 6 into 2 blocks
        """
        mu = _to_minimaj_blocks(t)
        if mu in self:
            return self(mu)
        else:
            raise AssertionError("%s is not an element of %s"%(mu, self))

    def val(self, q='q'):
        """
        Return `Val` polynomial corresponding to ``self``.

        EXAMPLES:

        Verifying Example 4.5 from [BCHOPSY2017]_::

            sage: B = crystals.Minimaj(3, 4, 2) # for `Val_{4,1}^{(3)}`
            sage: B.val()
            (q^2+q+1)*s[2, 1, 1] + q*s[2, 2]
        """
        H = [self._OMPs(list(b)) for b in self.highest_weight_vectors()]
        Sym = SymmetricFunctions(ZZ[q])
        q = Sym.base_ring().gens()[0]
        s = Sym.schur()
        return sum((q**(t.minimaj()) * s[sorted(t.weight().values(), reverse=True)]
                   for t in H), Sym.zero())

    class Element(ElementWrapper):
        r"""
        An element of a Minimaj crystal.

        .. NOTE::

            Minimaj elements `b` are stored internally as pairs `(w, breaks)`, where:
            - `w` is a word of length ``self.parent().ell`` over the letters
                `1` up to ``self.parent().n``;
            - `breaks` is a list of de-concatenation points to turn `w` into a list
                of row words of (skew-)tableaux that represent `b` under the minimaj
                bijection `\varphi` of [BCHOPSY2017]_.
            The pair `(w, breaks)` may be recovered via ``b.value``
        """
        def _repr_(self):
            """
            Return the string representation of ``self``.
            """
            return repr(self._minimaj_blocks_from_word_pair())

        def __iter__(self):
            """
            Iterate over ``self._minimaj_blocks_from_word_pair()``.
            """
            return self._minimaj_blocks_from_word_pair().__iter__()

        def _minimaj_blocks_from_word_pair(self):
            """
            Return the tuple of tuples (in the minimaj ordering on blocks
            of ordered multiset partitions) corresponding to ``self``.
            """
            return _to_minimaj_blocks(self.to_tableau())

        def to_tableau(self):
            r"""
            Return the image of the ordered multiset partition ``self`` under
            the minimaj bijection `\varphi` of [BCHOPSY2017]_.

            EXAMPLES::

                sage: B = crystals.Minimaj(4,5,3)
                sage: b = B.an_element(); b
                ((4, 1, 3), (3,), (3,))
                sage: b.to_tableau()
                [[3, 1], [], [4, 3, 3]]
            """
            w, breaks = self.value
            return [[ZZ(w[a].value) for a in range(breaks[j], breaks[j+1])]
                        for j in range(len(breaks)-1)]

        def e(self, i):
            r"""
            Return `e_i` on ``self``.

            EXAMPLES::

                sage: B = crystals.Minimaj(4,3,2)
                sage: b = B.an_element(); b
                ((2, 3), (3,))
                sage: [b.e(i) for i in range(1,4)]
                [((1, 3), (3,)), ((2,), (2, 3)), None]
            """
            P = self.parent()
            w, breaks = self.value
            if w.e(i) is None:
                return None
            w = w.e(i)
            return P.element_class(P, (w, breaks))

        def f(self,i):
            r"""
            Return `f_i` on ``self``.

            EXAMPLES::

                sage: B = crystals.Minimaj(4,3,2)
                sage: b = B.an_element(); b
                ((2, 3), (3,))
                sage: [b.f(i) for i in range(1,4)]
                [None, None, ((2, 3), (4,))]
            """
            P = self.parent()
            w, breaks = self.value
            if w.f(i) is None:
                return None
            w = w.f(i)
            return P.element_class(P, (w, breaks))

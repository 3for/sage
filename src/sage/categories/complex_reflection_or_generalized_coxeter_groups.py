r"""
Generalized Coxeter Groups
"""
#*****************************************************************************
#  Copyright (C) 2016 Travis Scrimshaw <tscrim at ucdavis.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

import itertools
from sage.misc.abstract_method import abstract_method
from sage.misc.cachefunc import cached_method
from sage.categories.category_singleton import Category_singleton
from sage.categories.category_with_axiom import CategoryWithAxiom, axiom
from sage.categories.groups import Groups

class ComplexReflectionOrGeneralizedCoxeterGroups(Category_singleton):
    r"""
    The category of complex reflection groups or generalized coxeter groups.

    Finite Coxeter groups can be defined equivalently as groups
    generated by reflections, or by presentations. Over the last
    decades, the theory has been generalized in both directions,
    leading to the study of complex reflection groups on the one hand,
    and generalized Coxeter groups on the other hand. Many of the
    features remain similar, yet, in the current state of the art,
    there is no general theory covering both directions.

    This is reflected by the name of this category which is about
    factoring out the common code, tests, and declarations.

    .. TODO:: Describe the common features

    .. SEEALSO::

        - :class:`complex_reflection_groups.ComplexReflectionGroups`
        - :class:`generalized_coxeter_groups.GeneralizedCoxeterGroups`

    EXAMPLES::

        sage: from sage.categories.complex_reflection_or_generalized_coxeter_groups import ComplexReflectionOrGeneralizedCoxeterGroups
        sage: C = ComplexReflectionOrGeneralizedCoxeterGroups(); C
        Category of complex reflection or generalized coxeter groups
        sage: C.super_categories()
        [Category of finitely generated groups]

    TESTS::

        sage: TestSuite(C).run()
    """

    @cached_method
    def super_categories(self):
        r"""
        Return the super categories of ``self``.

        EXAMPLES::

            sage: from sage.categories.complex_reflection_groups import ComplexReflectionGroups
            sage: ComplexReflectionGroups().super_categories()
            [Category of complex reflection or generalized coxeter groups]
        """
        return [Groups().FinitelyGenerated()]

    class SubcategoryMethods:
        def Irreducible(self):
            r"""
            Return the full subcategory of irreducible objects of ``self``.

            A complex reflection group, or generalized coxeter group
            is *reducible* if its simple reflections can be split in
            two sets `X` and `Y` such that the elements of `X` commute
            with that of `Y`. In particular, the group is then direct
            product of `\langle X\rangle` and `\langle Y\rangle`. It's
            *irreducible* otherwise.

            EXAMPLES::

                sage: from sage.categories.complex_reflection_groups import ComplexReflectionGroups
                sage: ComplexReflectionGroups().Irreducible()
                Category of irreducible complex reflection groups
                sage: CoxeterGroups().Irreducible()
                Category of irreducible coxeter groups

            TESTS::

                sage: TestSuite(ComplexReflectionGroups().Irreducible()).run()
                sage: CoxeterGroups().Irreducible.__module__
                'sage.categories.complex_reflection_or_generalized_coxeter_groups'
            """
            return self._with_axiom('Irreducible')

    class ParentMethods:
        @abstract_method
        def index_set(self):
            r"""
            Return the index set of (the simple reflections of)
            ``self``, as a list (or iterable).

            EXAMPLES::

                sage: W = CoxeterGroups().Finite().example(); W
                The 5-th dihedral group of order 10
                sage: W.index_set()
                (1, 2)

                sage: W = ColoredPermutations(1, 4)
                sage: W.index_set()
                (1, 2, 3)
                sage: W = ReflectionGroup((1,1,4), index_set=[1,3,'asdf'])
                sage: W.index_set()
                (1, 3, 'asdf')
                sage: W = ReflectionGroup((1,1,4), index_set=('a','b','c'))
                sage: W.index_set()
                ('a', 'b', 'c')
            """
            # return self.simple_reflections().keys()

        def simple_reflection(self, i):
            """
            Return the `i`-th simple reflection `s_i` of ``self``.

            INPUT:

            - ``i`` -- an element from the index set

            EXAMPLES::

                sage: W = CoxeterGroups().example()
                sage: W
                The symmetric group on {0, ..., 3}
                sage: W.simple_reflection(1)
                (0, 2, 1, 3)
                sage: s = W.simple_reflections()
                sage: s[1]
                (0, 2, 1, 3)

                sage: W = ReflectionGroup((1,1,4), index_set=[1,3,'asdf'])
                sage: for i in W.index_set():
                ....:     print('%s %s'%(i, W.simple_reflection(i)))
                1 (1,7)(2,4)(5,6)(8,10)(11,12)
                3 (1,4)(2,8)(3,5)(7,10)(9,11)
                asdf (2,5)(3,9)(4,6)(8,11)(10,12)
            """
            if not i in self.index_set():
                raise ValueError("%s is not in the Dynkin node set %s" % (i, self.index_set()))
            return self.one().apply_simple_reflection(i)  # don't care about left/right

        @cached_method
        def simple_reflections(self):
            r"""
            Return the simple reflections `(s_i)_{i\in I}` of ``self`` as a family
            indexed by :meth:`index_set`.

            EXAMPLES:

            For the symmetric group, we recognize the simple transpositions::

                sage: W = SymmetricGroup(4); W
                Symmetric group of order 4! as a permutation group
                sage: s = W.simple_reflections()
                sage: s
                Finite family {1: (1,2), 2: (2,3), 3: (3,4)}
                sage: s[1]
                (1,2)
                sage: s[2]
                (2,3)
                sage: s[3]
                (3,4)

            Here are the simple reflections for a colored symmetric
            group and a reflection group::

                sage: W = ColoredPermutations(1,3)
                sage: W.simple_reflections()
                Finite family {1: [[0, 0, 0], [2, 1, 3]], 2: [[0, 0, 0], [1, 3, 2]]}

                sage: W = ReflectionGroup((1,1,3), index_set=['a','b'])
                sage: W.simple_reflections()
                Finite family {'a': (1,4)(2,3)(5,6), 'b': (1,3)(2,5)(4,6)}

            This default implementation uses :meth:`.index_set` and
            :meth:`.simple_reflection`.
            """
            from sage.sets.family import Family
            return Family(self.index_set(), self.simple_reflection)

        def number_of_simple_reflections(self):
            r"""
            Return the number of simple reflections of ``self``.

            EXAMPLES::

                sage: W = ColoredPermutations(1,3)
                sage: W.number_of_simple_reflections()
                2
                sage: W = ColoredPermutations(2,3)
                sage: W.number_of_simple_reflections()
                3
                sage: W = ColoredPermutations(4,3)
                sage: W.number_of_simple_reflections()
                3
                sage: W = ReflectionGroup((4,2,3))
                sage: W.number_of_simple_reflections()
                4
            """
            return len(self.index_set())

        ##########################################################################
        # Group generators, etc from simple reflections
        ##########################################################################

        def group_generators(self):
            r"""
            Return the simple reflections of ``self``, as
            distinguished group generators.

            .. SEEALSO::

                - :meth:`simple_reflections`
                - :meth:`Groups.ParentMethods.group_generators`
                - :meth:`Semigroups.ParentMethods.semigroup_generators`

            EXAMPLES::

                sage: D10 = FiniteCoxeterGroups().example(10)
                sage: D10.group_generators()
                Finite family {1: (1,), 2: (2,)}
                sage: SymmetricGroup(5).group_generators()
                Finite family {1: (1,2), 2: (2,3), 3: (3,4), 4: (4,5)}

                sage: W = ColoredPermutations(3,2)
                sage: W.group_generators()
                Finite family {1: [[0, 0],
                                   [2, 1]],
                               2: [[0, 1],
                                   [1, 2]]}

            The simple reflections are also semigroup generators, even
            for an infinite group::

                sage: W = WeylGroup(["A",2,1])
                sage: W.semigroup_generators()
                Finite family {0: [-1  1  1]
                                  [ 0  1  0]
                                  [ 0  0  1],
                               1: [ 1  0  0]
                                  [ 1 -1  1]
                                  [ 0  0  1],
                               2: [ 1  0  0]
                                  [ 0  1  0]
                                  [ 1  1 -1]}
            """
            return self.simple_reflections()

        semigroup_generators = group_generators

        def simple_reflection_orders(self):
            """
            Return the orders of the simple reflections.

            EXAMPLES::

                sage: W = WeylGroup(['B',3])
                sage: W.simple_reflection_orders()
                [2, 2, 2]
                sage: W = CoxeterGroup(['C',4])
                sage: W.simple_reflection_orders()
                [2, 2, 2, 2]
                sage: SymmetricGroup(5).simple_reflection_orders()
                [2, 2, 2, 2]
                sage: C = ColoredPermutations(4, 3)
                sage: C.simple_reflection_orders()
                [2, 2, 4]
            """
            one = self.one()
            s = self.simple_reflections()
            from sage.rings.all import ZZ

            def mult_order(x):
                ct = ZZ.one()
                cur = x
                while cur != one:
                    cur *= x
                    ct += ZZ.one()
                return ZZ(ct)
            return [mult_order(s[i]) for i in self.index_set()]

        def _an_element_(self):
            """
            Implement: :meth:`Sets.ParentMethods.an_element` by
            returning the product of the simple reflections (a Coxeter
            element).

            EXAMPLES::

                sage: W = SymmetricGroup(4); W
                Symmetric group of order 4! as a permutation group
                sage: W.an_element()               # indirect doctest
                (1,2,3,4)

            For a complex reflection group::

                sage: from sage.categories.complex_reflection_groups import ComplexReflectionGroups
                sage: W = ComplexReflectionGroups().example(); W
                5-colored permutations of size 3
                sage: W.an_element()
                [[1, 0, 0], [3, 1, 2]]
            """
            return self.prod(self.simple_reflections())

        def some_elements(self):
            r"""
            Implement :meth:`Sets.ParentMethods.some_elements` by
            returning some typical elements of ``self``.

            EXAMPLES::

                sage: W = WeylGroup(['A',3])
                sage: W.some_elements()
                [
                [0 1 0 0]  [1 0 0 0]  [1 0 0 0]  [1 0 0 0]  [0 0 0 1]
                [1 0 0 0]  [0 0 1 0]  [0 1 0 0]  [0 1 0 0]  [1 0 0 0]
                [0 0 1 0]  [0 1 0 0]  [0 0 0 1]  [0 0 1 0]  [0 1 0 0]
                [0 0 0 1], [0 0 0 1], [0 0 1 0], [0 0 0 1], [0 0 1 0]
                ]
                sage: W.order()
                24
            """
            return list(self.simple_reflections()) + [self.one(), self.an_element()]

        ##########################################################################
        # Reflections
        ##########################################################################

        @abstract_method(optional=True)
        def reflection_index_set(self):
            r"""
            Return the index set of the reflections of ``self``.

            EXAMPLES::

                sage: W = ReflectionGroup((1,1,4))
                sage: W.reflection_index_set()
                (1, 2, 3, 4, 5, 6)
                sage: W = ReflectionGroup((1,1,4), reflection_index_set=[1,3,'asdf',7,9,11])
                sage: W.reflection_index_set()
                (1, 3, 'asdf', 7, 9, 11)
                sage: W = ReflectionGroup((1,1,4), reflection_index_set=('a','b','c','d','e','f'))
                sage: W.reflection_index_set()
                ('a', 'b', 'c', 'd', 'e', 'f')
            """

        @abstract_method(optional=True)
        def reflection(self, i):
            r"""
            Return the `i`-th reflection of ``self``.

            For `i` in `1,\dots,N`, this gives the `i`-th reflection of
            ``self``.

            EXAMPLES::

                sage: W = ReflectionGroup((1,1,4))
                sage: for i in W.reflection_index_set():
                ....:     print('%s %s'%(i, W.reflection(i)))
                1 (1,7)(2,4)(5,6)(8,10)(11,12)
                2 (1,4)(2,8)(3,5)(7,10)(9,11)
                3 (2,5)(3,9)(4,6)(8,11)(10,12)
                4 (1,8)(2,7)(3,6)(4,10)(9,12)
                5 (1,6)(2,9)(3,8)(5,11)(7,12)
                6 (1,11)(3,10)(4,9)(5,7)(6,12)
            """

        @cached_method
        def reflections(self):
            r"""
            Return a finite family containing the reflections of
            ``self``, indexed by :meth:`reflection_index_set`.

            EXAMPLES::

                sage: W = ReflectionGroup((1,1,3))
                sage: reflections = W.reflections()
                sage: for index in sorted(reflections.keys()):
                ....:     print('%s %s'%(index, reflections[index]))
                1 (1,4)(2,3)(5,6)
                2 (1,3)(2,5)(4,6)
                3 (1,5)(2,4)(3,6)

                sage: W = ReflectionGroup((1,1,3),reflection_index_set=['a','b','c'])
                sage: reflections = W.reflections()
                sage: for index in sorted(reflections.keys()):
                ....:     print('%s %s'%(index, reflections[index]))
                a (1,4)(2,3)(5,6)
                b (1,3)(2,5)(4,6)
                c (1,5)(2,4)(3,6)

                sage: W = ReflectionGroup((3,1,1))
                sage: reflections = W.reflections()
                sage: for index in sorted(reflections.keys()):
                ....:     print('%s %s'%(index, reflections[index]))
                1 (1,2,3)
                2 (1,3,2)

                sage: W = ReflectionGroup((1,1,3), (3,1,2))
                sage: reflections = W.reflections()
                sage: for index in sorted(reflections.keys()):
                ....:     print('%s %s'%(index, reflections[index]))
                1 (1,6)(2,5)(7,8)
                2 (1,5)(2,7)(6,8)
                3 (3,9,15)(4,10,16)(12,17,23)(14,18,24)(20,25,29)(21,22,26)(27,28,30)
                4 (3,11)(4,12)(9,13)(10,14)(15,19)(16,20)(17,21)(18,22)(23,27)(24,28)(25,26)(29,30)
                5 (1,7)(2,6)(5,8)
                6 (3,19)(4,25)(9,11)(10,17)(12,28)(13,15)(14,30)(16,18)(20,27)(21,29)(22,23)(24,26)
                7 (4,21,27)(10,22,28)(11,13,19)(12,14,20)(16,26,30)(17,18,25)(23,24,29)
                8 (3,13)(4,24)(9,19)(10,29)(11,15)(12,26)(14,21)(16,23)(17,30)(18,27)(20,22)(25,28)
                9 (3,15,9)(4,16,10)(12,23,17)(14,24,18)(20,29,25)(21,26,22)(27,30,28)
                10 (4,27,21)(10,28,22)(11,19,13)(12,20,14)(16,30,26)(17,25,18)(23,29,24)
            """
            from sage.sets.family import Family
            return Family(self.reflection_index_set(), self.reflection)

        ##########################################################################
        # Distinguished reflections
        ##########################################################################

        @abstract_method(optional=True)
        def distinguished_reflection(self, i):
            r"""
            Return the `i`-th distinguished reflection of ``self``.

            For `i` in `1,\dots,N^*`, this gives the `i`-th distinguished reflection of ``self``.
            For a definition of distinguished reflections, see :meth:`distinguished_reflections`.

            EXAMPLES::

                sage: W = ReflectionGroup((1,1,4), hyperplane_index_set=('a','b','c','d','e','f'))
                sage: for i in W.hyperplane_index_set():
                ....:     print('%s %s'%(i, W.distinguished_reflection(i)))
                a (1,7)(2,4)(5,6)(8,10)(11,12)
                b (1,4)(2,8)(3,5)(7,10)(9,11)
                c (2,5)(3,9)(4,6)(8,11)(10,12)
                d (1,8)(2,7)(3,6)(4,10)(9,12)
                e (1,6)(2,9)(3,8)(5,11)(7,12)
                f (1,11)(3,10)(4,9)(5,7)(6,12)
            """

        @cached_method
        def distinguished_reflections(self):
            r"""
            Return a finite family containing the distinguished
            reflections of ``self``, indexed by
            :meth:`hyperplane_index_set`.

            A *distinguished reflection* is a conjugate of a simple
            reflection. For a Coxeter group, reflections and
            distinguished reflections coincide. For a Complex
            reflection groups this is a reflection acting on the
            complement of the fixed hyperplane `H` as
            `\operatorname{exp}(2 \pi i / n)`, where `n` is the order
            of the reflection subgroup fixing `H`.


            EXAMPLES::

                sage: W = ReflectionGroup((1,1,3))
                sage: distinguished_reflections = W.distinguished_reflections()
                sage: for index in sorted(distinguished_reflections.keys()):
                ....:     print('%s %s'%(index, distinguished_reflections[index]))
                1 (1,4)(2,3)(5,6)
                2 (1,3)(2,5)(4,6)
                3 (1,5)(2,4)(3,6)

                sage: W = ReflectionGroup((1,1,3),hyperplane_index_set=['a','b','c'])
                sage: distinguished_reflections = W.distinguished_reflections()
                sage: for index in sorted(distinguished_reflections.keys()):
                ....:     print('%s %s'%(index, distinguished_reflections[index]))
                a (1,4)(2,3)(5,6)
                b (1,3)(2,5)(4,6)
                c (1,5)(2,4)(3,6)

                sage: W = ReflectionGroup((3,1,1))
                sage: distinguished_reflections = W.distinguished_reflections()
                sage: for index in sorted(distinguished_reflections.keys()):
                ....:     print('%s %s'%(index, distinguished_reflections[index]))
                1 (1,2,3)

                sage: W = ReflectionGroup((1,1,3), (3,1,2))
                sage: distinguished_reflections = W.distinguished_reflections()
                sage: for index in sorted(distinguished_reflections.keys()):
                ....:     print('%s %s'%(index, distinguished_reflections[index]))
                1 (1,6)(2,5)(7,8)
                2 (1,5)(2,7)(6,8)
                3 (3,9,15)(4,10,16)(12,17,23)(14,18,24)(20,25,29)(21,22,26)(27,28,30)
                4 (3,11)(4,12)(9,13)(10,14)(15,19)(16,20)(17,21)(18,22)(23,27)(24,28)(25,26)(29,30)
                5 (1,7)(2,6)(5,8)
                6 (3,19)(4,25)(9,11)(10,17)(12,28)(13,15)(14,30)(16,18)(20,27)(21,29)(22,23)(24,26)
                7 (4,21,27)(10,22,28)(11,13,19)(12,14,20)(16,26,30)(17,18,25)(23,24,29)
                8 (3,13)(4,24)(9,19)(10,29)(11,15)(12,26)(14,21)(16,23)(17,30)(18,27)(20,22)(25,28)
            """
            from sage.sets.family import Family
            return Family(self.hyperplane_index_set(), self.distinguished_reflection)

        ##########################################################################
        # Irreducible components
        ##########################################################################

        def from_word(self, word, word_type='simple'):
            r"""
            Return the reflection group element corresponding to
            ``word``.

            INPUT:

            - ``word`` -- a list (or iterable) of elements of the
              appropriate index set

            - ``word_type`` -- (optional, default: ``'simple'``) can be
              ``'simple'``, ``'distinguished'``, or ``'all'``, depending
              on the type of reflections used

            If ``word`` is `[i_1, i_2, \ldots, i_k]`, then this returns the
            corresponding product of (simple/distinguished/all)
            reflections `t_{i_1} t_{i_2} \cdots t_{i_k}`.

            EXAMPLES::

                sage: W = ColoredPermutations(1,4)
                sage: W.from_word([1,2,1,2,1,2])
                [[0, 0, 0, 0], [1, 2, 3, 4]]

                sage: W.from_word([1, 2, 3]).reduced_word()
                [1, 2, 3]

                sage: W = ReflectionGroup((1,1,4))
                sage: W.from_word([1,2,3], word_type='all').reduced_word()
                [1, 2, 3]

                sage: W.from_word([1,2,3], word_type='all').reduced_word_in_reflections()
                [1, 2, 3]

                sage: W.from_word([1,2,3]).reduced_word_in_reflections()
                [1, 2, 3]
            """
            if word_type == 'simple':
                f = self.one().apply_simple_reflections
            elif word_type == 'distinguished':
                f = self.one().apply_distinguished_reflections
            elif word_type == 'all':
                f = self.one().apply_reflections
            return f(word, side='right')

        ##########################################################################
        # Irreducible components
        ##########################################################################

        def irreducible_component_index_sets(self):
            r"""
            Return a list containing the index sets of the irreducible components of
            ``self`` as finite reflection groups.

            EXAMPLES::

                sage: W = ReflectionGroup([1,1,3], [3,1,3], 4); W
                Reducible complex reflection group of rank 7 and type A2 x G(3,1,3) x ST4
                sage: sorted(W.irreducible_component_index_sets())
                [[1, 2], [3, 4, 5], [6, 7]]

            ALGORITHM:

                Take the connected components of the graph on the
                index set with edges (i,j) where s[i] and s[j] don't
                commute.
            """
            I = self.index_set()
            s = self.simple_reflections()
            from sage.graphs.graph import Graph
            G = Graph([I,
                       [[i,j]
                        for i,j in itertools.combinations(I,2)
                        if s[i]*s[j] != s[j]*s[i] ]],
                      format="vertices_and_edges")
            return G.connected_components()

        @abstract_method(optional=True)
        def irreducible_components(self):
            r"""
            Return the irreducible components of ``self`` as finite
            reflection groups.

            EXAMPLES::

                sage: W = ReflectionGroup([1,1,3], [3,1,3], 4)
                sage: W.irreducible_components()
                [Irreducible real reflection group of rank 2 and type A2,
                 Irreducible complex reflection group of rank 3 and type G(3,1,3),
                 Irreducible complex reflection group of rank 2 and type ST4]
            """
            # TODO: provide a default implementation using the above and parabolic subgroups

        def number_of_irreducible_components(self):
            r"""
            Return the number of irreducible components of ``self``.

            EXAMPLES::

                sage: W = ColoredPermutations(1,3)
                sage: W.number_of_irreducible_components()
                1

                sage: W = ReflectionGroup((1,1,3),(2,1,3))
                sage: W.number_of_irreducible_components()
                2
            """
            return len(self.irreducible_components())

        def is_irreducible(self):
            r"""
            Return ``True`` if ``self`` is irreducible.

            EXAMPLES::

                sage: W = ColoredPermutations(1,3); W
                1-colored permutations of size 3
                sage: W.is_irreducible()
                True

                sage: W = ReflectionGroup((1,1,3),(2,1,3)); W
                Reducible real reflection group of rank 5 and type A2 x B3
                sage: W.is_irreducible()
                False
            """
            return self.number_of_irreducible_components() == 1

        def is_reducible(self):
            r"""
            Return ``True`` if ``self`` is not irreducible.

            EXAMPLES::

                sage: W = ColoredPermutations(1,3); W
                1-colored permutations of size 3
                sage: W.is_reducible()
                False

                sage: W = ReflectionGroup((1,1,3), (2,1,3)); W
                Reducible real reflection group of rank 5 and type A2 x B3
                sage: W.is_reducible()
                True
            """
            return not self.is_irreducible()


    class ElementMethods:
        # TODO: standardize / cleanup
        # TODO: Combine with similar methods in ComplexReflectionGroups
        # at least one of the two methods must be reimplemented
        # it is recommended to reimplement both, as computing
        # the inverse might not be very efficient...
        def apply_simple_reflection_left(self, i):
            r"""
            Return ``self`` multiplied by the simple reflection ``s[i]``
            on the left.

            This low level method is used intensively. Coxeter groups
            are encouraged to override this straightforward
            implementation whenever a faster approach exists.

            EXAMPLES::

                sage: W = CoxeterGroups().example()
                sage: w = W.an_element(); w
                (1, 2, 3, 0)
                sage: w.apply_simple_reflection_left(0)
                (0, 2, 3, 1)
                sage: w.apply_simple_reflection_left(1)
                (2, 1, 3, 0)
                sage: w.apply_simple_reflection_left(2)
                (1, 3, 2, 0)

            EXAMPLES::

                sage: from sage.categories.complex_reflection_groups import ComplexReflectionGroups
                sage: W = ComplexReflectionGroups().example()
                sage: w = W.an_element(); w
                [[1, 0, 0], [3, 1, 2]]
                sage: w.apply_simple_reflection_left(1)
                [[0, 1, 0], [1, 3, 2]]
                sage: w.apply_simple_reflection_left(2)
                [[1, 0, 0], [3, 2, 1]]
                sage: w.apply_simple_reflection_left(3)
                [[1, 0, 1], [3, 1, 2]]

            TESTS::

                sage: w.apply_simple_reflection_left.__module__
                'sage.categories.complex_reflection_or_generalized_coxeter_groups'
            """
            s = self.parent().simple_reflections()
            return s[i] * self

        def apply_simple_reflection_right(self, i):
            """
            Return ``self`` multiplied by the simple reflection ``s[i]``
            on the right.

            This low level method is used intensively. Coxeter groups
            are encouraged to override this straightforward
            implementation whenever a faster approach exists.

            EXAMPLES::

                sage: W=CoxeterGroups().example()
                sage: w = W.an_element(); w
                (1, 2, 3, 0)
                sage: w.apply_simple_reflection_right(0)
                (2, 1, 3, 0)
                sage: w.apply_simple_reflection_right(1)
                (1, 3, 2, 0)
                sage: w.apply_simple_reflection_right(2)
                (1, 2, 0, 3)

                sage: from sage.categories.complex_reflection_groups import ComplexReflectionGroups
                sage: W = ComplexReflectionGroups().example()
                sage: w = W.an_element(); w
                [[1, 0, 0], [3, 1, 2]]
                sage: w.apply_simple_reflection_right(1)
                [[1, 0, 0], [3, 2, 1]]
                sage: w.apply_simple_reflection_right(2)
                [[1, 0, 0], [2, 1, 3]]
                sage: w.apply_simple_reflection_right(3)
                [[2, 0, 0], [3, 1, 2]]

            TESTS::

                sage: w.apply_simple_reflection_right.__module__
                'sage.categories.complex_reflection_or_generalized_coxeter_groups'
            """
            s = self.parent().simple_reflections()
            return self * s[i]

        def apply_simple_reflection(self, i, side='right'):
            """
            Return ``self`` multiplied by the simple reflection ``s[i]``.

            INPUT:

            - ``i`` -- an element of the index set
            - ``side`` -- (default: ``"right"``) ``"left"`` or ``"right"``

            This default implementation simply calls
            :meth:`apply_simple_reflection_left` or
            :meth:`apply_simple_reflection_right`.

            EXAMPLES::

                sage: W = CoxeterGroups().example()
                sage: w = W.an_element(); w
                (1, 2, 3, 0)
                sage: w.apply_simple_reflection(0, side = "left")
                (0, 2, 3, 1)
                sage: w.apply_simple_reflection(1, side = "left")
                (2, 1, 3, 0)
                sage: w.apply_simple_reflection(2, side = "left")
                (1, 3, 2, 0)

                sage: w.apply_simple_reflection(0, side = "right")
                (2, 1, 3, 0)
                sage: w.apply_simple_reflection(1, side = "right")
                (1, 3, 2, 0)
                sage: w.apply_simple_reflection(2, side = "right")
                (1, 2, 0, 3)

            By default, ``side`` is "right"::

                sage: w.apply_simple_reflection(0)
                (2, 1, 3, 0)

            Some tests with a complex reflection group::

                sage: from sage.categories.complex_reflection_groups import ComplexReflectionGroups
                sage: W = ComplexReflectionGroups().example(); W
                5-colored permutations of size 3
                sage: w = W.an_element(); w
                [[1, 0, 0], [3, 1, 2]]
                sage: w.apply_simple_reflection(1, side="left")
                [[0, 1, 0], [1, 3, 2]]
                sage: w.apply_simple_reflection(2, side="left")
                [[1, 0, 0], [3, 2, 1]]
                sage: w.apply_simple_reflection(3, side="left")
                [[1, 0, 1], [3, 1, 2]]

                sage: w.apply_simple_reflection(1, side="right")
                [[1, 0, 0], [3, 2, 1]]
                sage: w.apply_simple_reflection(2, side="right")
                [[1, 0, 0], [2, 1, 3]]
                sage: w.apply_simple_reflection(3, side="right")
                [[2, 0, 0], [3, 1, 2]]

            TESTS::

                sage: w.apply_simple_reflection_right.__module__
                'sage.categories.complex_reflection_or_generalized_coxeter_groups'
            """
            if side == 'right':
                return self.apply_simple_reflection_right(i)
            else:
                return self.apply_simple_reflection_left(i)

        def apply_simple_reflections(self, word, side='right'):
            """
            Return the result of the (left/right) multiplication of
            ``self`` by ``word``.

            INPUT:

            - ``word`` -- a sequence of indices of simple reflections
            - ``side`` -- (default: ``'right'``) indicates multiplying
              from left or right

            EXAMPLES::

               sage: W = CoxeterGroups().example()
               sage: w = W.an_element(); w
               (1, 2, 3, 0)
               sage: w.apply_simple_reflections([0,1])
               (2, 3, 1, 0)
               sage: w
               (1, 2, 3, 0)
               sage: w.apply_simple_reflections([0,1],side='left')
               (0, 1, 3, 2)
            """
            for i in word:
                self = self.apply_simple_reflection(i, side)
            return self

        def _mul_(self, other):
            r"""
            Return the product of ``self`` and ``other``

            This default implementation computes a reduced word of
            ``other`` using :meth:`reduced_word`, and applies the
            corresponding simple reflections on ``self`` using
            :meth:`apply_simple_reflections`.

            EXAMPLES::

                sage: W = FiniteCoxeterGroups().example(); W
                The 5-th dihedral group of order 10
                sage: w = W.an_element()
                sage: w
                (1, 2)
                sage: w._mul_(w)
                (1, 2, 1, 2)
                sage: w._mul_(w)._mul_(w)
                (2, 1, 2, 1)

            This method is called when computing ``self * other``::

                sage: w * w
                (1, 2, 1, 2)

            TESTS::

                sage: w._mul_.__module__
                'sage.categories.complex_reflection_or_generalized_coxeter_groups'
            """
            return self.apply_simple_reflections(other.reduced_word())

        def inverse(self):
            """
            Return the inverse of ``self``.

            EXAMPLES::

                sage: W = WeylGroup(['B',7])
                sage: w = W.an_element()
                sage: u = w.inverse()
                sage: u == ~w
                True
                sage: u * w == w * u
                True
                sage: u * w
                [1 0 0 0 0 0 0]
                [0 1 0 0 0 0 0]
                [0 0 1 0 0 0 0]
                [0 0 0 1 0 0 0]
                [0 0 0 0 1 0 0]
                [0 0 0 0 0 1 0]
                [0 0 0 0 0 0 1]
            """
            return self.parent().one().apply_simple_reflections(self.reduced_word_reverse_iterator())

        __invert__ = inverse

        def apply_conjugation_by_simple_reflection(self, i):
            r"""
            Conjugate ``self`` by the ``i``-th simple reflection.

            EXAMPLES::

                sage: W = WeylGroup(['A',3])
                sage: w = W.from_reduced_word([3,1,2,1])
                sage: w.apply_conjugation_by_simple_reflection(1).reduced_word()
                [3, 2]
            """
            return (self.apply_simple_reflection(i)).apply_simple_reflection(i, side='left')

        @abstract_method(optional=True)
        def reflection_length(self):
            r"""
            Return the reflection length of ``self``.

            This is the minimal length of a factorization of ``self``
            into reflections.

            EXAMPLES::

                sage: W = ReflectionGroup((1,1,2))
                sage: sorted([t.reflection_length() for t in W])
                [0, 1]

                sage: W = ReflectionGroup((2,1,2))
                sage: sorted([t.reflection_length() for t in W])
                [0, 1, 1, 1, 1, 2, 2, 2]

                sage: W = ReflectionGroup((3,1,2))
                sage: sorted([t.reflection_length() for t in W])
                [0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]

                sage: W = ReflectionGroup((2,2,2))
                sage: sorted([t.reflection_length() for t in W])
                [0, 1, 1, 2]
            """

        def is_reflection(self):
            r"""
            Return ``True`` if ``self`` is a reflection.

            EXAMPLES::

                sage: W = ReflectionGroup((1,1,4))
                sage: [t.is_reflection() for t in W.reflections()]
                [True, True, True, True, True, True]
                sage: len([t for t in W.reflections() if t.is_reflection()])
                6

                sage: W = ReflectionGroup((2,1,3))
                sage: [t.is_reflection() for t in W.reflections()]
                [True, True, True, True, True, True, True, True, True]
                sage: len([t for t in W.reflections() if t.is_reflection()])
                9
            """
            return self.reflection_length() == 1


    class Irreducible(CategoryWithAxiom):
        class ParentMethods:
            def irreducible_components(self):
                r"""
                Return a list containing all irreducible components of
                ``self`` as finite reflection groups.

                EXAMPLES::

                    sage: W = ColoredPermutations(4, 3)
                    sage: W.irreducible_components()
                    [4-colored permutations of size 3]
                """
                return [self]

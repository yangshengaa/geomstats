import pytest

import geomstats.backend as gs
from geomstats.test.test_case import TestCase
from geomstats.test.vectorization import generate_vectorization_data


class ManifoldTestCase(TestCase):
    # TODO: remove random_tangent_vec?
    # TODO: remove regularize

    def test_belongs(self, point, expected, atol):
        res = self.space.belongs(point)
        self.assertAllEqual(res, expected)

    @pytest.mark.vec
    def test_belongs_vec(self, n_reps, atol):
        # TODO: remove? random_point_belongs is enough
        point = self.space.random_point()
        res = self.space.belongs(point)

        vec_data = generate_vectorization_data(
            data=[dict(point=point, expected=res, atol=atol)],
            arg_names=["point"],
            expected_name="expected",
            n_reps=n_reps,
        )

        for datum in vec_data:
            self.test_belongs(**datum)

    @pytest.mark.random
    def test_not_belongs(self, n_points, atol):
        shape = list(self.space.shape)
        shape[0] += 1

        n_batch = [n_points] if n_points else []
        point = gs.ones(n_batch + shape)
        expected = gs.zeros(n_points, dtype=bool)

        self.test_belongs(point, expected, atol)

    @pytest.mark.random
    def test_random_point_belongs(self, n_points, atol):
        point = self.space.random_point(n_points)
        expected = gs.ones(n_points, dtype=bool)

        self.test_belongs(point, expected, atol)

    @pytest.mark.shape
    def test_random_point_shape(self, n_points):
        point = self.space.random_point(n_points)

        expected_ndim = self.space.point_ndim + int(n_points > 1)
        self.assertEqual(gs.ndim(point), expected_ndim)

        self.assertAllEqual(gs.shape(point)[-self.space.point_ndim :], self.space.shape)

        if n_points > 1:
            self.assertEqual(gs.shape(point)[0], n_points)

    def test_is_tangent(self, vector, base_point, expected, atol):
        res = self.space.is_tangent(vector, base_point, atol=atol)
        self.assertAllEqual(res, expected)

    def test_to_tangent(self, vector, base_point, expected, atol):
        tangent_vec = self.space.to_tangent(vector, base_point)
        self.assertAllClose(tangent_vec, expected, atol=atol)


class VectorSpaceTestCase(ManifoldTestCase):
    # TODO: test projection

    @pytest.mark.vec
    def test_is_tangent_vec(self, n_reps, atol):
        vec = self.space.random_point()
        point = self.space.random_point()

        tangent_vec = self.space.to_tangent(vec, point)
        res = self.space.is_tangent(tangent_vec, point)

        vec_data = generate_vectorization_data(
            data=[dict(vector=tangent_vec, base_point=point, expected=res, atol=atol)],
            arg_names=["vector", "base_point"],
            expected_name="expected",
            n_reps=n_reps,
            vectorization_type="sym",
        )
        for datum in vec_data:
            self.test_is_tangent(**datum)

    @pytest.mark.vec
    def test_to_tangent_vec(self, n_reps, atol):
        vec = self.space.random_point()
        point = self.space.random_point()

        res = self.space.to_tangent(vec, point)

        vec_data = generate_vectorization_data(
            data=[dict(vector=vec, base_point=point, expected=res, atol=atol)],
            arg_names=["vector", "base_point"],
            expected_name="expected",
            n_reps=n_reps,
            vectorization_type="sym",
        )
        for datum in vec_data:
            self.test_to_tangent(**datum)

    @pytest.mark.random
    def test_to_tangent_is_tangent(self, n_points, atol):
        vec = self.space.random_point(n_points)
        point = self.space.random_point(n_points)

        tangent_vec = self.space.to_tangent(vec, point)
        expected = gs.ones(n_points, dtype=bool)

        self.test_is_tangent(tangent_vec, point, expected, atol)

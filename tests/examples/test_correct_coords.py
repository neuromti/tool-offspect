from offspect.examples.correct_coords import calculate_translation
from pytest import raises


def test_translation_both():
    translation = calculate_translation([[-36, -17, 54], [36, -17, 54]])
    assert translation == [[0.63, 0.677, -0.315], [-0.63, 0.677, -0.315]]


def test_translation_default():
    translation = calculate_translation()
    assert translation == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]


def test_translation_right():
    translation = calculate_translation([[36, -17, 54]])
    assert translation == [[0.0, 0.0, 0.0], [-0.63, 0.677, -0.315]]


def test_translation_left():
    translation = calculate_translation([[-36, -17, 54]])
    assert translation == [[0.63, 0.677, -0.315], [0.0, 0.0, 0.0]]

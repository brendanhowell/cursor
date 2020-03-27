from cursor import path

import pyautogui
import pytest


def test_pathcollection_minmax():
    pcol = path.PathCollection()

    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(10, 11, 10001)
    p1.add(11, 11, 10002)
    p1.add(20, 20, 10003)
    p1.add(30, 31, 10004)
    p1.add(40, 41, 10005)

    p2 = path.Path()

    p2.add(545, 54, 10000)
    p2.add(160, 11, 10001)
    p2.add(11, 171, 10002)
    p2.add(20, 20, 10003)
    p2.add(30, 31, 10004)
    p2.add(940, 941, 10005)

    pcol.add(p1)
    pcol.add(p2)

    assert pcol.empty() is False

    min = pcol.min()
    max = pcol.max()
    bb = pcol.bb()

    assert min[0] == bb.x
    assert min[1] == bb.y
    assert max[0] == bb.w + bb.x
    assert max[1] == bb.h + bb.y

    assert min[0] == 5
    assert min[1] == 11
    assert max[0] == 940
    assert max[1] == 5111


def test_pathcollection_add():
    pcol = path.PathCollection()

    assert pcol.empty() is True

    p1 = path.Path()

    pcol.add(p1)

    assert pcol.empty() is True


def test_pathcollection_add2():
    pcol1 = path.PathCollection()
    p1 = path.Path()
    p1.add(5, 5111, 10000)
    p1.add(10, 11, 10001)
    pcol1.add(p1)

    pcol2 = path.PathCollection()
    p2 = path.Path()
    p2.add(545, 54, 10000)
    p2.add(160, 11, 10001)
    pcol2.add(p2)

    pcol3 = pcol1 + pcol2

    assert len(pcol3) == 2

    pcol4 = pcol1 + pcol2.get_all() + pcol2.get_all()

    assert len(pcol4) == 3

    with pytest.raises(Exception):
        _ = pcol1 + p1


def test_pathcollection_get():
    pcol = path.PathCollection()

    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(40, 41, 10005)

    pcol.add(p1)

    p2 = pcol[0]

    assert p1 == p2

    with pytest.raises(IndexError):
        pcol[1]


def test_pathcollection_compare():
    pcol = path.PathCollection()
    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(40, 41, 10005)

    pcol.add(p1)

    pcol2 = path.PathCollection()
    r = pcol == pcol2

    assert not r


def test_pathcollection_clean():
    pcol = path.PathCollection()
    p0 = path.Path()

    p0.add(5, 5111, 10000)

    p1 = path.Path()

    p1.add(5, 5111, 10000)
    p1.add(40, 41, 10005)

    pcol.add(p0)
    pcol.add(p1)

    assert len(pcol) == 2

    pcol.clean()

    assert len(pcol) == 1

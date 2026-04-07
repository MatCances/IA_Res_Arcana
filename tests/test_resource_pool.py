import pytest
from utils.resource_pool import ResourcePool
from utils.constant import Resource


@pytest.fixture
def pool():
    return ResourcePool()


# --- add / remove ---

def test_add_augmente_la_ressource(pool):
    pool.add(Resource.GOLD, 3)
    assert pool.resources[Resource.GOLD] == 3


def test_add_par_defaut_ajoute_1(pool):
    pool.add(Resource.LIFE)
    assert pool.resources[Resource.LIFE] == 1


def test_remove_diminue_la_ressource(pool):
    pool.add(Resource.DEATH, 4)
    pool.remove(Resource.DEATH, 2)
    assert pool.resources[Resource.DEATH] == 2


def test_remove_par_defaut_enleve_1(pool):
    pool.add(Resource.CALM, 2)
    pool.remove(Resource.CALM)
    assert pool.resources[Resource.CALM] == 1


def test_remove_trop_leve_value_error(pool):
    pool.add(Resource.ELAN, 1)
    with pytest.raises(ValueError):
        pool.remove(Resource.ELAN, 2)


def test_remove_sur_zero_leve_value_error(pool):
    with pytest.raises(ValueError):
        pool.remove(Resource.GOLD, 1)


# --- has ---

def test_has_true_si_assez(pool):
    pool.add(Resource.GOLD, 3)
    assert pool.has(Resource.GOLD, 3) is True


def test_has_false_si_pas_assez(pool):
    pool.add(Resource.GOLD, 2)
    assert pool.has(Resource.GOLD, 3) is False


def test_has_defaut_amount_1(pool):
    pool.add(Resource.LIFE, 1)
    assert pool.has(Resource.LIFE) is True


def test_has_any_utilise_le_total(pool):
    pool.add(Resource.GOLD, 2)
    pool.add(Resource.ELAN, 1)
    assert pool.has(Resource.ANY, 3) is True
    assert pool.has(Resource.ANY, 4) is False


def test_has_any_exclut_pearl(pool):
    pool.add(Resource.PEARL, 5)
    assert pool.has(Resource.ANY, 1) is False


# --- total ---

def test_total_somme_sans_pearl(pool):
    pool.add(Resource.GOLD, 2)
    pool.add(Resource.LIFE, 3)
    pool.add(Resource.PEARL, 10)
    assert pool.total == 5


def test_total_zero_si_vide(pool):
    assert pool.total == 0


# --- available ---

def test_available_retourne_ressources_non_nulles(pool):
    pool.add(Resource.GOLD, 1)
    pool.add(Resource.CALM, 2)
    result = pool.available()
    assert Resource.GOLD in result
    assert Resource.CALM in result
    assert Resource.LIFE not in result


def test_available_exclut_any_par_defaut(pool):
    pool.add(Resource.GOLD, 1)
    result = pool.available()
    assert Resource.ANY not in result


def test_available_avec_excluded(pool):
    pool.add(Resource.GOLD, 1)
    pool.add(Resource.LIFE, 1)
    result = pool.available(excluded={Resource.GOLD})
    assert Resource.GOLD not in result
    assert Resource.LIFE in result


def test_available_vide_si_aucune_ressource(pool):
    assert pool.available() == []


# --- get_amount ---

def test_get_amount_retourne_valeur(pool):
    pool.add(Resource.PEARL, 5)
    assert pool.get_amount(Resource.PEARL) == 5


def test_get_amount_zero_si_aucune(pool):
    assert pool.get_amount(Resource.DEATH) == 0

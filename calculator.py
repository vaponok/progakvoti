"""
Калькулятор ресурсов для заводского заказа.

Модель — первоуровневые материалы:
  м1, м2, м3, обр., стр.мат., Обогащённое топливо (fuel), редкие

Высокоуровневые раскладываются:
  м4    → обр. ×1
  р.сплав → обр. ×5 + редкие ×20 + кокс ×60
  сталь → обр. ×3 + кокс ×125 + fuel ×1
  м5    → м1 ×10 + м2 ×10 + обр. ×9 + кокс ×245 + сталь×3

Гибкие рецепты (per-unit):
  coke_recipe: "with_sulfur" → 200 угля = 165 кокса + 15 серы побочно
               "no_sulfur"   → 200 угля = 180 кокса
  fuel_recipe: "coal"   → 100 угля = 1 топливо
               "sulfur" → 60 серы  = 1 топливо
  scrap_ratio: 0.0..1.0 → доля обр. через металлолом

Первоуровневые в базовых ресурсах:
  м1:   75 кокса + 15 металлолома
  м2:   15 металлолома
  м3:   20 серы  + 15 металлолома
  обр.: 95 металлолома ИЛИ 18.(3) компонентов + 5 металлолома
  стр.: 5 металлолома
  fuel: 100 угля ИЛИ 60 серы
  редкие: базовый, не дробятся
"""

import math
from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# BaseCost — стоимость в базовых ресурсах
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class BaseCost:
    coal:             int = 0
    scrap:            int = 0
    components:       int = 0
    sulfur:           int = 0
    rare_mats:        int = 0
    sulfur_byproduct: int = 0  # побочная сера от кокса

    def __add__(self, other: "BaseCost") -> "BaseCost":
        return BaseCost(
            coal=self.coal + other.coal,
            scrap=self.scrap + other.scrap,
            components=self.components + other.components,
            sulfur=self.sulfur + other.sulfur,
            rare_mats=self.rare_mats + other.rare_mats,
            sulfur_byproduct=self.sulfur_byproduct + other.sulfur_byproduct,
        )

    def net_sulfur(self) -> int:
        """Сера к покупке с учётом побочки от кокса."""
        return max(0, self.sulfur - self.sulfur_byproduct)

    def sulfur_surplus(self) -> int:
        return max(0, self.sulfur_byproduct - self.sulfur)


# ──────────────────────────────────────────────────────────────────────────────
# FirstLevelMats — первоуровневые материалы после раскладки
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class FirstLevelMats:
    m1:    int = 0
    m2:    int = 0
    m3:    int = 0
    proc:  int = 0
    build: int = 0
    fuel:  int = 0
    rare:  int = 0
    coke:  int = 0   # кокс (базовый, переводится в уголь)


def expand_to_first_level(costs: dict) -> FirstLevelMats:
    """Раскладывает рецепт товара до первоуровневых материалов."""
    s = {k: int(costs.get(k, 0)) for k in
         ("steel", "m1", "m2", "m3", "m4", "m5", "proc", "rare", "build")}
    fl = FirstLevelMats()

    # м5: каждый м5 = 3 стали + 245 кокса + 10 м1 + 10 м2
    # 3 стали = 9 обр. + 375 кокса + 3 топлива
    fl.m1   += s["m5"] * 10
    fl.m2   += s["m5"] * 10
    fl.proc += s["m5"] * 9
    fl.coke += s["m5"] * (245 + 375)
    fl.fuel += s["m5"] * 3

    # сталь: ceil(n/3) батчей, каждый батч = 9 обр. + 375 кокса + 3 топлива
    if s["steel"] > 0:
        batches = math.ceil(s["steel"] / 3)
        fl.proc += batches * 9
        fl.coke += batches * 375
        fl.fuel += batches * 3

    # р.сплав → обр.×5 + редкие×20 + кокс×60
    fl.proc += s["rare"] * 5
    fl.rare += s["rare"] * 20
    fl.coke += s["rare"] * 60

    # м4 → обр.×1
    fl.proc += s["m4"]

    # прямые
    fl.m1   += s["m1"]
    fl.m2   += s["m2"]
    fl.m3   += s["m3"]
    fl.proc += s["proc"]
    fl.build += s["build"]

    return fl


# ──────────────────────────────────────────────────────────────────────────────
# Стоимость каждого первоуровневого материала
# ──────────────────────────────────────────────────────────────────────────────

def _coal_for_coke(coke_needed: int, coke_recipe: str) -> BaseCost:
    if coke_needed <= 0:
        return BaseCost()
    per_batch = 165 if coke_recipe == "with_sulfur" else 180
    batches   = math.ceil(coke_needed / per_batch)
    return BaseCost(
        coal=batches * 200,
        sulfur_byproduct=batches * 15 if coke_recipe == "with_sulfur" else 0,
    )


def cost_m1(count: int, coke_recipe: str) -> BaseCost:
    ck = _coal_for_coke(count * 75, coke_recipe)
    return BaseCost(coal=ck.coal, scrap=count * 15,
                    sulfur_byproduct=ck.sulfur_byproduct)


def cost_m2(count: int) -> BaseCost:
    return BaseCost(scrap=count * 15)


def cost_m3(count: int) -> BaseCost:
    return BaseCost(sulfur=count * 20, scrap=count * 15)


def cost_proc(count: int, scrap_ratio: float) -> BaseCost:
    via_scrap = round(count * scrap_ratio)
    via_comp  = count - via_scrap
    return BaseCost(
        scrap=via_scrap * 95 + via_comp * 5,
        components=round(via_comp * (55 / 3)),
    )


def cost_build(count: int) -> BaseCost:
    return BaseCost(scrap=count * 5)


def cost_fuel(count: int, fuel_recipe: str) -> BaseCost:
    if fuel_recipe == "sulfur":
        return BaseCost(sulfur=count * 60)
    return BaseCost(coal=count * 100)


def cost_rare(count: int) -> BaseCost:
    return BaseCost(rare_mats=count)


# ──────────────────────────────────────────────────────────────────────────────
# MatDetail — детальный расчёт по материалу
# ──────────────────────────────────────────────────────────────────────────────

MAT_NAMES = {
    "m1":    "1-е материалы",
    "m2":    "2-е материалы",
    "m3":    "3-и материалы",
    "proc":  "Обработанные",
    "build": "Стр. материалы",
    "fuel":  "Обогащённое топливо",
    "rare":  "Редкие материалы",
}

MAT_ORDER = ["m1", "m2", "m3", "proc", "build", "fuel", "rare"]


@dataclass
class MatDetail:
    mat_key:  str
    mat_name: str
    count:    int
    cost:     BaseCost
    paid:     dict = field(default_factory=dict)  # {"scrap": N, "coal": M, ...}


def calculate_detail(
    costs: dict,
    coke_recipe: str = "with_sulfur",
    fuel_recipe: str = "coal",
    scrap_ratio: float = 0.0,
) -> list:
    """Детальный расчёт по каждому первоуровневому материалу."""
    fl = expand_to_first_level(costs)
    details = []

    if fl.m1 > 0:
        c = cost_m1(fl.m1, coke_recipe)
        details.append(MatDetail("m1", MAT_NAMES["m1"], fl.m1, c))

    if fl.m2 > 0:
        details.append(MatDetail("m2", MAT_NAMES["m2"], fl.m2, cost_m2(fl.m2)))

    if fl.m3 > 0:
        details.append(MatDetail("m3", MAT_NAMES["m3"], fl.m3, cost_m3(fl.m3)))

    if fl.proc > 0:
        details.append(MatDetail("proc", MAT_NAMES["proc"], fl.proc,
                                 cost_proc(fl.proc, scrap_ratio)))

    if fl.build > 0:
        details.append(MatDetail("build", MAT_NAMES["build"], fl.build,
                                 cost_build(fl.build)))

    if fl.fuel > 0:
        details.append(MatDetail("fuel", MAT_NAMES["fuel"], fl.fuel,
                                 cost_fuel(fl.fuel, fuel_recipe)))

    if fl.rare > 0:
        details.append(MatDetail("rare", MAT_NAMES["rare"], fl.rare,
                                 cost_rare(fl.rare)))

    # Кокс без привязки к материалу (из р.сплав, сталь, м5 — уже растворён в coal выше)
    # Дополнительный кокс не нужен — он уже учтён в cost_m1, cost_proc через _coal_for_coke

    return details


def total_cost(
    costs: dict,
    coke_recipe: str = "with_sulfur",
    fuel_recipe: str = "coal",
    scrap_ratio: float = 0.0,
) -> BaseCost:
    details = calculate_detail(costs, coke_recipe, fuel_recipe, scrap_ratio)
    result = BaseCost()
    for d in details:
        result = result + d.cost

    # Кокс из м1 и других — уже в coal. Но кокс который НЕ в м1
    # (из стали, м5, р.сплав) тоже нужно перевести в уголь.
    # Он уже включён через expand + _coal_for_coke в каждом cost_* через fl.coke.
    # Но fl.coke сам по себе не переводится — добавим его отдельно:
    fl = expand_to_first_level(costs)
    # Кокс уже включён в cost_m1 (75 кокса на м1), но fl.coke содержит кокс
    # из стали/м5/р.сплав — он не привязан к материалу, добавляем вручную:
    # На самом деле в calculate_detail кокс из стали/м5/р.сплав НЕ включён
    # т.к. нет отдельного MatDetail для него. Добавим его в угль:
    extra_coke_cost = _coal_for_coke(fl.coke, coke_recipe)
    result.coal += extra_coke_cost.coal
    result.sulfur_byproduct += extra_coke_cost.sulfur_byproduct

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Расчёт остатка с учётом оплат по материалам
# ──────────────────────────────────────────────────────────────────────────────

def remaining_detail(
    costs: dict,
    payments_by_mat: dict,
    coke_recipe: str = "with_sulfur",
    fuel_recipe: str = "coal",
    scrap_ratio: float = 0.0,
) -> list:
    """
    payments_by_mat: {"proc": {"scrap": 4000, "components": 0}, "m1": {"coal": 500}, ...}
    Возвращает список MatDetail с остатком в cost.
    """
    fl = expand_to_first_level(costs)
    details = []

    def _simple_rem(mat_key, full_cost: BaseCost, count: int) -> BaseCost:
        paid = payments_by_mat.get(mat_key, {})
        return BaseCost(
            coal=max(0, full_cost.coal - paid.get("coal", 0)),
            scrap=max(0, full_cost.scrap - paid.get("scrap", 0)),
            components=max(0, full_cost.components - paid.get("components", 0)),
            sulfur=max(0, full_cost.sulfur - paid.get("sulfur", 0)),
            rare_mats=max(0, full_cost.rare_mats - paid.get("rare_mats", 0)),
            sulfur_byproduct=full_cost.sulfur_byproduct,
        )

    if fl.m1 > 0:
        full = cost_m1(fl.m1, coke_recipe)
        paid = payments_by_mat.get("m1", {})
        details.append(MatDetail("m1", MAT_NAMES["m1"], fl.m1,
                                 _simple_rem("m1", full, fl.m1), paid))

    if fl.m2 > 0:
        full = cost_m2(fl.m2)
        paid = payments_by_mat.get("m2", {})
        details.append(MatDetail("m2", MAT_NAMES["m2"], fl.m2,
                                 _simple_rem("m2", full, fl.m2), paid))

    if fl.m3 > 0:
        full = cost_m3(fl.m3)
        paid = payments_by_mat.get("m3", {})
        details.append(MatDetail("m3", MAT_NAMES["m3"], fl.m3,
                                 _simple_rem("m3", full, fl.m3), paid))

    if fl.proc > 0:
        paid = payments_by_mat.get("proc", {})
        rem_cost = _remaining_proc(fl.proc, paid, scrap_ratio)
        details.append(MatDetail("proc", MAT_NAMES["proc"], fl.proc, rem_cost, paid))

    if fl.build > 0:
        full = cost_build(fl.build)
        paid = payments_by_mat.get("build", {})
        details.append(MatDetail("build", MAT_NAMES["build"], fl.build,
                                 _simple_rem("build", full, fl.build), paid))

    if fl.fuel > 0:
        paid = payments_by_mat.get("fuel", {})
        rem_cost = _remaining_fuel(fl.fuel, paid, fuel_recipe)
        details.append(MatDetail("fuel", MAT_NAMES["fuel"], fl.fuel, rem_cost, paid))

    if fl.rare > 0:
        full = cost_rare(fl.rare)
        paid = payments_by_mat.get("rare", {})
        details.append(MatDetail("rare", MAT_NAMES["rare"], fl.rare,
                                 _simple_rem("rare", full, fl.rare), paid))

    return details


def _remaining_proc(count: int, paid: dict, scrap_ratio: float) -> BaseCost:
    """
    Остаток обработанных с учётом смены рецепта.
    - Скрап: 95 = 1 обр. через скрап, 5 = фикс на компонентный путь
    - Компоненты: 55/3 ≈ 18.33 = 1 обр.
    """
    paid_scrap = paid.get("scrap", 0)
    paid_comp  = paid.get("components", 0)

    # Закрытые через скрап (по 95)
    closed_via_scrap = paid_scrap // 95
    leftover_scrap   = paid_scrap % 95

    # Закрытые через компоненты (по 55/3)
    comp_per_proc = 55 / 3
    closed_via_comp = int(paid_comp // comp_per_proc)

    closed_total  = min(count, closed_via_scrap + closed_via_comp)
    remaining_cnt = max(0, count - closed_total)

    if remaining_cnt == 0:
        return BaseCost()

    rem = cost_proc(remaining_cnt, scrap_ratio)
    # Огрызок скрапа вычитаем из оставшегося скрапа
    rem.scrap = max(0, rem.scrap - leftover_scrap)
    return rem


def _remaining_fuel(count: int, paid: dict, fuel_recipe: str) -> BaseCost:
    if fuel_recipe == "sulfur":
        paid_sulfur = paid.get("sulfur", 0)
        closed = paid_sulfur // 60
        return BaseCost(sulfur=max(0, count - closed) * 60)
    else:
        paid_coal = paid.get("coal", 0)
        closed = paid_coal // 100
        return BaseCost(coal=max(0, count - closed) * 100)


def total_remaining(
    costs: dict,
    payments_by_mat: dict,
    coke_recipe: str = "with_sulfur",
    fuel_recipe: str = "coal",
    scrap_ratio: float = 0.0,
) -> BaseCost:
    details = remaining_detail(costs, payments_by_mat, coke_recipe, fuel_recipe, scrap_ratio)
    fl = expand_to_first_level(costs)
    result = BaseCost()
    for d in details:
        result = result + d.cost
    # Добавляем уголь на кокс из стали/м5/р.сплав
    # Считаем сколько кокса уже оплачено (через м1 и другие материалы)
    # Простой подход: берём кокс из total_cost и вычитаем то что уже в деталях
    extra_coke_cost = _coal_for_coke(fl.coke, coke_recipe)
    # Вычитаем оплаченный уголь на этот кокс
    paid_extra_coal = payments_by_mat.get("_extra_coke", {}).get("coal", 0)
    result.coal += max(0, extra_coke_cost.coal - paid_extra_coal)
    result.sulfur_byproduct += extra_coke_cost.sulfur_byproduct
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Обратная совместимость (старый API)
# ──────────────────────────────────────────────────────────────────────────────

def calculate_order(
    costs: dict,
    coke_recipe: str = "with_sulfur",
    fuel_recipe: str = "coal",
    scrap_ratio: float = 0.0,
) -> dict:
    tc     = total_cost(costs, coke_recipe, fuel_recipe, scrap_ratio)
    tc_min = total_cost(costs, coke_recipe, fuel_recipe, 0.0)
    fl     = expand_to_first_level(costs)

    proc_via_scrap = round(fl.proc * scrap_ratio)
    proc_via_comp  = fl.proc - proc_via_scrap

    return {
        "coal":               tc.coal,
        "sulfur_buy":         tc.net_sulfur(),
        "sulfur_byproduct":   tc.sulfur_byproduct,
        "scrap_fixed":        tc_min.scrap,
        "scrap_dynamic":      max(0, tc.scrap - tc_min.scrap),
        "scrap_total":        tc.scrap,
        "components":         tc.components,
        "rare_mats":          tc.rare_mats,
        "fuel_needed":        fl.fuel,
        "fuel_recipe":        fuel_recipe,
        "processed_total":    fl.proc,
        "processed_via_scrap": proc_via_scrap,
        "processed_via_comp":  proc_via_comp,
        "sulfur_surplus":     tc.sulfur_surplus(),
    }


def remaining(
    costs: dict,
    already_brought: dict,
    coke_recipe: str = "with_sulfur",
    fuel_recipe: str = "coal",
    scrap_ratio: float = 0.0,
) -> dict:
    needed = calculate_order(costs, coke_recipe, fuel_recipe, scrap_ratio)
    b = already_brought
    return {
        "coal":       max(0, needed["coal"]       - b.get("coal", 0)),
        "sulfur_buy": max(0, needed["sulfur_buy"] - b.get("sulfur", 0)),
        "scrap_fixed":   needed["scrap_fixed"],
        "scrap_dynamic": needed["scrap_dynamic"],
        "scrap_total":   max(0, needed["scrap_total"]  - b.get("scrap", 0)),
        "components":    max(0, needed["components"]   - b.get("components", 0)),
        "rare_mats":     max(0, needed["rare_mats"]    - b.get("rare_mats", 0)),
        "fuel_needed":   max(0, needed["fuel_needed"]  - b.get("fuel", 0)),
        "fuel_recipe":   fuel_recipe,
        "processed_total":     needed["processed_total"],
        "processed_via_scrap": needed["processed_via_scrap"],
        "processed_via_comp":  needed["processed_via_comp"],
        "coke_produced":       0,
        "sulfur_byproduct":    needed["sulfur_byproduct"],
        "sulfur_surplus":      needed["sulfur_surplus"],
    }


VARIANTS = [
    (0.00, "100% компоненты"),
    (0.25, "25% скрап / 75% компоненты"),
    (0.50, "50/50"),
    (0.75, "75% скрап / 25% компоненты"),
    (1.00, "100% металлолом"),
]

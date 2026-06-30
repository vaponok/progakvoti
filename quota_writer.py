#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quota_writer.py — UI для написания квоты (переработанный)
- фикс. кнопки 150x150, spacing=10, columns=6
- последняя страница (p==11) — белый фон
- навигационные кнопки и image-кнопки имеют одинаковые скругления (маска + stylesheet)
- поддержка PyInstaller через resource_path
"""

import sys
import os
from math import ceil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTextEdit, QLabel, QStackedWidget, QScrollArea, QSpinBox
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPainterPath, QRegion
from PyQt5.QtCore import Qt, QSize, QRectF

# ---- helper for resources (works in normal run and in onefile exe) ----
def resource_path(relative_path: str) -> str:
    """
    Return path to resource, works for dev and for PyInstaller onefile bundle.
    Use resource_path("images/foo.png") everywhere you load files.
    """
    if getattr(sys, "_MEIPASS", None):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)
# ----------------------------------------------------------------------

# Configuration: number of buttons per page
PAGE_BUTTON_COUNTS = [24, 22, 12, 23, 1, 5, 9, 35, 11, 4, 44, 12]
# Default image path pattern (you can change these paths later)
IMAGE_PATH_PATTERN = os.path.join("images", "p{page}_b{idx}.png")
BUTTON_SIZE = QSize(150, 150)  # strict button size as requested
BUTTON_SPACING = 10  # strict spacing between buttons
COLUMNS = 6

# EXTRA WIDTH for the fixed box (user requested +30px)
EXTRA_WIDTH = 30

# rounded radius used everywhere
ROUNDED_RADIUS = 6.0

# image paths (relative paths; resource_path will convert them for exe)
IMAGE_MAPPING = {
    # --- page 1 ---
    'p1_b1': "images/Booker_Storm_Rifle_Model_838.png",
    'p1_b2': "images/Aalto_Storm_Rifle_24.png",
    'p1_b3': "images/7_92mm.png",
    'p1_b4': "images/Malone_MK_2.png",
    'p1_b5': "images/A3_Harpa_Fragmentation_Grenade.png",
    'p1_b6': "images/Cascadier_873.png",
    'p1_b7': "images/8mm.png",
    'p1_b8': "images/Cometa_T2_9.png",
    'p1_b9': "images/The_Hangman_757.png",
    'p1_b10': "images/44.png",
    'p1_b11': "images/Sampo_Auto_Rifle_77.png",
    'p1_b12': "images/Blakerow_871.png",
    'p1_b13': "images/Clancy_Cinder_M3.png",
    'p1_b14': "images/No_2B_Hawthorne.png",
    'p1_b15': "images/No_2_Loughcaster.png",
    'p1_b16': "images/7_62mm.png",
    'p1_b17': "images/No_4_The_Pillary_Scattergun.png",
    'p1_b18': "images/Buckshot.png",
    'p1_b19': "images/No_1_The_Liar_Submachine_Gun.png",
    'p1_b20': "images/Fiddler_Submachine_Gun_Model_868.png",
    'p1_b21': "images/9mm_SMG.png",
    'p1_b22': "images/PT_815_Smoke_Grenade.png",
    'p1_b23': "images/Green_Ash_Grenade.png",
    'p1_b24': "images/12_7mm.png",
    # --- page 2 ---
    'p2_b1': "images/135_Neville_Anti_Tank_Rifle.png",
    'p2_b2': "images/20mm.png",
    'p2_b3': "images/Carnyx_Anti_Tank_Rocket_Launcher.png",
    'p2_b4': "images/A_T_R_P_G_Shell.png",
    'p2_b5': "images/Mounted_Bonesaw_MK_3.png",
    'p2_b6': "images/Bonesaw_MK_3.png",
    'p2_b7': "images/A_T_R_P_G_Indirect_Shell.png",
    'p2_b8': "images/Willows_Bane_Model_845.png",
    'p2_b9': "images/Tremola_Grenade_GPb_1.png",
    'p2_b10': "images/Malone_Ratcatcher_MK_1.png",
    'p2_b11': "images/30mm.png",
    'p2_b12': "images/Cremari_Mortar.png",
    'p2_b13': "images/Mortar_Shell_Flare.png",
    'p2_b14': "images/Mortar_Shell_Shrapnel.png",
    'p2_b15': "images/Mortar_Shell.png",
    'p2_b16': "images/BF5_White_Ash_Flask_Grenade.png",
    'p2_b17': "images/B2_Varsi_Anti_Tank_Grenade.png",
    'p2_b18': "images/Mammon_91_b.png",
    'p2_b19': "images/Anti_Tank_Sticky_Bomb.png",
    'p2_b20': "images/Cutler_Foebreaker.png",
    'p2_b21': "images/Cutler_Launcher_4.png",
    'p2_b22': "images/R_P_G_Shell.png",
    # --- page 3 ---
    'p3_b1': "images/950-70b Anti-Aircraft Shell.png",
    'p3_b2': "images/20мм.png",
    'p3_b3': "images/Shatter Missile.png",
    'p3_b4': "images/150mm.png",
    'p3_b5': "images/LightAAAmmoIcon.png",
    'p3_b6': "images/120mm.png",
    'p3_b7': "images/Quillback Torpedo.png",
    'p3_b8': "images/250mm.png",
    'p3_b9': "images/250mm Fury Shell.png",
    'p3_b10': "images/E681-B Hullbreaker Mine.png",
    'p3_b11': "images/68mm.png",
    'p3_b12': "images/40mm.png",
    # --- page 4 ---
    'p4_b1': "images/Barbed_Wire.png",
    'p4_b2': "images/Buckhorn_CCQ_18.png",
    'p4_b3': "images/Binoculars.png",
    'p4_b4': "images/Havoc_Charge.png",
    'p4_b5': "images/Willows_Bane_Ammo.png",
    'p4_b6': "images/Listening_Kit.png",
    'p4_b7': "images/Falias_Raiding_Club.png",
    'p4_b8': "images/Metal_Beam.png",
    'p4_b9': "images/Radio_Backpack.png",
    'p4_b10': "images/Sandbag.png",
    'p4_b11': "images/Havoc_Charge_Detonator.png",
    'p4_b12': "images/Alligator_Charge.png",
    'p4_b13': "images/Shovel.png",
    'p4_b14': "images/Sledge_Hammer.png",
    'p4_b15': "images/Tripod.png",
    'p4_b16': "images/Wind_Sock.png",
    'p4_b17': "images/Wrench.png",
    'p4_b18': "images/Water_Bucket.png",
    'p4_b19': "images/Gas_Mask.png",
    'p4_b20': "images/Gas_Mask_Filter.png",
    'p4_b21': "images/The_Ospreay.png",
    'p4_b22': "images/Radio.png",
    'p4_b23': "images/Liaison Transmitter.png",
    # --- page 5 ---
    'p5_b1': "images/Maintenance_Supplies.png",
    # --- page 6 ---
    'p6_b1': "images/Bandages.png",
    'p6_b2': "images/First_Aid_kit.png",
    'p6_b3': "images/Trauma_Kit.png",
    'p6_b4': "images/Blood_Plasma.png",
    'p6_b5': "images/Soldier_Supplies.png",
    # --- page 7 ---
    'p7_b1': "images/Specialists_Overcoat.png",
    'p7_b2': "images/Gunners_Breastplate.png",
    'p7_b3': "images/Sapper_Gear.png",
    'p7_b4': "images/Physicians_Jacket.png",
    'p7_b5': "images/Gentlemans_Peacoat.png",
    'p7_b6': "images/Officers_Regalia.png",
    'p7_b7': "images/Outriders_Mantle.png",
    'p7_b8': "images/Caoivish_Parka.png",
    'p7_b9': "images/Padded_Boiler_Suit.png",
    # --- page 8 ---
    'p8_b1': "images/O_Brien_v_190_Knave.png",
    'p8_b2': "images/O_Brien_v_110.png",
    'p8_b3': "images/Noble_Widow_MK_XIV.png",
    'p8_b4': "images/Collins_Cannon_68mm.png",
    'p8_b5': "images/Balfour_Wolfhound_40mm.png",
    'p8_b6': "images/Swallowtail_988_127_2.png",
    'p8_b7': "images/Balfour_Falconer_250mm.png",
    'p8_b8': "images/Niska_Mk_I_Gun_Motor_Carriage.png",
    'p8_b9': "images/Mulloy_LPC.png",
    'p8_b10': "images/LightTank3WVehicleIcon.png",
    'p8_b11': "images/Devitt_Mk_III.png",
    'p8_b12': "images/Dunne_Responder_3e.png",
    'p8_b13': "images/Dunne_Caravaner_2F.png",
    'p8_b14': "images/BMS_Universal_Assemly_Rig.png",
    'p8_b15': "images/BMS_Class_2_Mobile_Auto_Crane.png",
    'p8_b16': "images/BMS_Packmule_Flatbed.png",
    'p8_b17': "images/Dunne_Fuelrunner_2d.png",
    'p8_b18': "images/Gallagher_Brigand_Mk_I.png",
    'p8_b19': "images/Silverhand_Mk_IV.png",
    'p8_b20': "images/Kivela_Power_Wheel_80_1.png",
    'p8_b21': "images/King_Spire_Mk_I.png",
    'p8_b22': "images/Drummond_100a.png",
    'p8_b23': "images/FuelTrailerIcon.png",
    'p8_b24': "images/MaterialTrailerIcon.png",
    'p8_b25': "images/Rooster_Junkwagon.png",
    'p8_b26': "images/Dunne_Loadlugger_3c.png",
    'p8_b27': "images/Dunne_Transport.png",
    'p8_b28': "images/81f-f Ronan Blackguard.png",
    'p8_b29': "images/74b_1_Ronan_Gunship.png",
    'p8_b30': "images/Das Krokodil by VAC.png",
    'p8_b31': "images/68A-4 Ronan Fathomer.png",
    'p8_b32': "images/BMS_Aquatipper.png",
    'p8_b33': "images/BMS_Ironship.png",
    'p8_b34': "images/Rinnspeir Ornitier-Class Gunship.png",
    'p8_b35': "images/Bellweather by VAC.png",
    # --- page 9 ---
    'p9_b1': "images/Material_Pallet.png",
    'p9_b2': "images/Resource_Container.png",
    'p9_b3': "images/Shipping_Container.png",
    'p9_b4': "images/Leary AA-70 Bolas.png",
    'p9_b5': "images/68mm_Anti_Tank_Cannon.png",
    'p9_b6': "images/Huber_Exalt_150mm.png",
    'p9_b7': "images/12_7_Anti_Infantry_Flak_Gun.png",
    'p9_b8': "images/Huber_Lariat_120mm.png",
    'p9_b9': "images/Concrete_Mixer.png",
    'p9_b10': "images/Construction_Equipment.png",
    'p9_b11': "images/Fuel_Container.png",
    # --- page 10 ---
    'p10_b1': "images/bmat.png",
    'p10_b2': "images/RefinedMaterialsIcon.png",
    'p10_b3': "images/ExplosiveMaterialIcon.png",
    'p10_b4': "images/100px-HeavyExplosiveMaterialsIcon.png",
    # --- page 11 ---
    'p11_b1': "images/AmbulanceFlameW.png",
    'p11_b2': "images/ArmoredCar2LargeW.png",
    'p11_b3': "images/ArmoredCar2MultiW.png",
    'p11_b4': "images/ArmoredCarATW.png",
    'p11_b5': "images/ArmoredCarFlameW.png",
    'p11_b6': "images/ATLargeAmmo-crated.png",
    'p11_b7': "images/ATRifleAssaultW-crated.png",
    'p11_b8': "images/ATRifleAutomaticW-crated.png",
    'p11_b9': "images/BattleTankAmmo-crated.png",
    'p11_b10': "images/ConstructionUtility.png",
    'p11_b11': "images/DepthChargeAmmo-crated.png",
    'p11_b12': "images/DestroyerTankFlameW.png",
    'p11_b13': "images/FacilityMaterials10-crated.png",
    'p11_b14': "images/FacilityMaterials9-crated.png",
    'p11_b15': "images/FieldATDamageW.png",
    'p11_b16': "images/FireRocketAmmo-crated.png",
    'p11_b17': "images/HalftrackMultiW.png",
    'p11_b18': "images/HalfTrackOffensiveW.png",
    'p11_b19': "images/HalfTrackTwinW.png",
    'p11_b20': "images/Harvester.png",
    'p11_b21': "images/HeavyTruckW.png",
    'p11_b22': "images/HERocketAmmo-crated.png",
    'p11_b23': "images/InfantryMine-crated.png",
    'p11_b24': "images/LargeFieldCannonW.png",
    'p11_b25': "images/LargeFieldMultiW.png",
    'p11_b26': "images/LightTankArtilleryW.png",
    'p11_b27': "images/LightTankDefensiveW.png",
    'p11_b28': "images/LRArtilleryAmmo-crated.png",
    'p11_b29': "images/MediumTank2IndirectW.png",
    'p11_b30': "images/MediumTank2MultiW.png",
    'p11_b31': "images/MediumTank2RangeW.png",
    'p11_b32': "images/MediumTankATW.png",
    'p11_b33': "images/MediumTankSiegeW.png",
    'p11_b34': "images/ScoutTankMultiW.png",
    'p11_b35': "images/ScoutTankOffensiveW.png",
    'p11_b36': "images/ScoutVehicleOffensiveW.png",
    'p11_b37': "images/ScoutVehicleUtilityW.png",
    'p11_b38': "images/TankMine-crated.png",
    'p11_b39': "images/TrailerLiquid.png",
    'p11_b40': "images/TrailerMaterial.png",
    'p11_b41': "images/TruckDefensiveW.png",
    'p11_b42': "images/TruckMobilityW.png",
    'p11_b43': "images/WaterMine-crated.png",
    'p11_b44': "images/MortarAmmoFlame-crated.png",
    # --- page 12 ---
    'p12_b1': "images/Tulka I1.9 White Raven.png",
    'p12_b2': "images/Luminary Mk. II Harbinger.png",
    'p12_b3': "images/M925 Austringer Man-O-War.png",
    'p12_b4': "images/Rinnspeir Mk. I Zealot.png",
    'p12_b5': "images/Tulka P4 Welkinrive.png",
    'p12_b6': "images/Warden Aircraft Mechanical Parts (Small).png",
    'p12_b7': "images/Warden Aircraft Mechanical Parts (Large).png",
    'p12_b8': "images/Warden Aircraft Engine (Small).png",
    'p12_b9': "images/Warden Aircraft Engine (Large).png",
    'p12_b10': "images/100px-ParatrooperUniformWIcon.png",
    'p12_b11': "images/100px-PilotUniformWIcon.png",
    'p12_b12': "images/100px-ParatrooperBackpackItemIcon.png",
}

ITEM_TEXT = {
    # --- page 1 ---
    'p1_b1': "Штурмовая винтовка Booker Model 838 (Ящик)",
    'p1_b2': "Штурмовая винтовка Aalto 24 (Ящик)",
    'p1_b3': "7.92-мм (Ящик)",
    'p1_b4': "Malone MK.2 (Ящик)",
    'p1_b5': "Осколочная граната A3 Harpa (Ящик)",
    'p1_b6': "Cascadier 873 (Ящик)",
    'p1_b7': "8-мм (Ящик)",
    'p1_b8': "Cometa T2-9 (Ящик)",
    'p1_b9': "Хангман 757 (Ящик)",
    'p1_b10': ".44 Mag (Ящик)",
    'p1_b11': "Автоматическая винтовка Sampo 77 (Ящик)",
    'p1_b12': "Blakerow 871 (Ящик)",
    'p1_b13': "Clancy Cinder M3 (Ящик)",
    'p1_b14': "No.2B Hawthorne (Ящик)",
    'p1_b15': "No.2 Loughcaster (Ящик)",
    'p1_b16': "7.62-мм (Ящик)",
    'p1_b17': "No.4 The Pillory Scattergun (Ящик)",
    'p1_b18': "Дробь (Ящик)",
    'p1_b19': "Пистолет-пулемет No.1 “The Liar” (Ящик)",
    'p1_b20': "Пистолет-пулемет Fiddler Model 868 (Ящик)",
    'p1_b21': "9-мм (Ящик)",
    'p1_b22': "Дымовая граната PT-815 (Ящик)",
    'p1_b23': "Газовая граната (Ящик)",
    'p1_b24': "12.7-мм (Ящик)",
    # --- page 2 ---
    'p2_b1': "Противотанковое ружье Neville  (Ящик)",
    'p2_b2': "14.5mm (Ящик)",
    'p2_b3': "РПГ \"Carnyx\" (Ящик)",
    'p2_b4': "Бронебойный/РПГ (Ящик)",
    'p2_b5': "Станковый Bonesaw MK.3 (Ящик)",
    'p2_b6': "Bonesaw MK.3 (Ящик)",
    'p2_b7': "Бронебойный навесной/РПГ (Ящик)",
    'p2_b8': "Willow’s Bane Model 845 (Ящик)",
    'p2_b9': "Граната Tremola Gpb-1 (Ящик)",
    'p2_b10': "Malone Ratcatcher MK.1 (Ящик)",
    'p2_b11': "30мм (Ящик)",
    'p2_b12': "Миномёт Cremari (Ящик)",
    'p2_b13': "Осветительный Минометный Снаряд (Ящик)",
    'p2_b14': "Осколочный минометный снаряд (Ящик)",
    'p2_b15': "Минометный Снаряд (Ящик)",
    'p2_b16': "Граната BF5 White Ash Flask (Ящик)",
    'p2_b17': "B2 Varsi Anti-Tank Grenade (Ящик)",
    'p2_b18': "Mammon 91-b (Ящик)",
    'p2_b19': "Противотанковая липкая бомба (Ящик)",
    'p2_b20': "Cutler Foebreaker (Ящик)",
    'p2_b21': "Cutler Launcher 4 (Ящик)",
    'p2_b22': "РПГ (Ящик)",
    # --- page 3 ---
    'p3_b1': "950-70b Anti-Aircraft Shell (Ящик)",
    'p3_b2': "20мм (Ящик)",
    'p3_b3': "Shatter Missile (Ящик)",
    'p3_b4': "150-мм (Ящик)",
    'p3_b5': "Absol Anti-Aircraft Rounds (Ящик)",
    'p3_b6': "120-мм (Ящик)",
    'p3_b7': "Quillback Torpedo (Ящик)",
    'p3_b8': "250mm \"Purity\" Shell (Ящик)",
    'p3_b9': "250mm \"Fury\" Shell (Ящик)",
    'p3_b10': "E681-B Hullbreaker Mine (Ящик)",
    'p3_b11': "68мм (Ящик)",
    'p3_b12': "40-мм (Ящик)",
    # --- page 4 ---
    'p4_b1': "Колючая проволока (Ящик)",
    'p4_b2': "Buckhorn CCQ-18 (Ящик)",
    'p4_b3': "Бинокль (Ящик)",
    'p4_b4': "Хавок Заряд (Ящик)",
    'p4_b5': "Топливо для Willow’s Bane (Ящик)",
    'p4_b6': "Набор для прослушивания (Ящик)",
    'p4_b7': "Falias Raiding Club (Ящик)",
    'p4_b8': "Металлическая балка (Ящик)",
    'p4_b9': "Радиорюкзак (Ящик)",
    'p4_b10': "Мешок с песком (Ящик)",
    'p4_b11': "Детонатор Хавок Заряда (Ящик)",
    'p4_b12': "Alligator Charge (Ящик)",
    'p4_b13': "Лопата (Ящик)",
    'p4_b14': "Кувалда (Ящик)",
    'p4_b15': "Тренога (Ящик)",
    'p4_b16': "Ветроуказатель (Ящик)",
    'p4_b17': "Гаечный ключ (Ящик)",
    'p4_b18': "Ведро для воды (Ящик)",
    'p4_b19': "Противогаз (Ящик)",
    'p4_b20': "Фильтр для противогаза (Ящик)",
    'p4_b21': "Подствольный гранатомёт (Ящик)",
    'p4_b22': "Рация (Ящик)",
    'p4_b23': "Liaison Transmitter (Ящик)",
    # --- page 5 ---
    'p5_b1': "Припасы Обслуживания (Ящик)",
    # --- page 6 ---
    'p6_b1': "Бинты (Ящик)",
    'p6_b2': "Набор Первой Помощи (Ящик)",
    'p6_b3': "Реанимационный набор (Ящик)",
    'p6_b4': "Плазма (Ящик)",
    'p6_b5': "Солдатское снаряжение (Ящик)",
    # --- page 7 ---
    'p7_b1': "Шинель специалиста (Ящик)",
    'p7_b2': "Стальная кираса (Ящик)",
    'p7_b3': "Сапёрное снаряжение (Ящик)",
    'p7_b4': "Куртка врача (Ящик)",
    'p7_b5': "Gentleman’s Peacoat (Ящик)",
    'p7_b6': "Офицерская регалия (Ящик)",
    'p7_b7': "Дозорная мантия (Ящик)",
    'p7_b8': "Парка Caoivish (Ящик)",
    'p7_b9': "Стеганный Комбинезон (Ящик)",
    # --- page 8 ---
    'p8_b1': "O’Brien V.190 Knave (Ящик)",
    'p8_b2': "O’Brien V.110 (Ящик)",
    'p8_b3': "Noble Widow MK. XIV (Ящик)",
    'p8_b4': "Collins орудие 68-мм (Ящик)",
    'p8_b5': "Balfour Wolfhound 40мм (Ящик)",
    'p8_b6': "Swallowtail 988/127-2 (Ящик)",
    'p8_b7': "Balfour Falconer 250-мм (Ящик)",
    'p8_b8': "Полугусеничный Бронетранспортер Niska Mk. I (Ящик)",
    'p8_b9': "Mulloy LPC (Ящик)",
    'p8_b10': "Sharkey-Devitt Birdeater Mk. I (Ящик)",
    'p8_b11': "Devitt Mk. III (Ящик)",
    'p8_b12': "Dunne Responder 3e (Ящик)",
    'p8_b13': "Dunne Caravaner 2f (Ящик)",
    'p8_b14': "BMS - Universal Assembly Rig (Ящик)",
    'p8_b15': "Мобильный автокран БМС 2 класса (Ящик)",
    'p8_b16': "Бортовой грузовик BMS - Packmule (Ящик)",
    'p8_b17': "Dunne Fuelrunner 2d (Ящик)",
    'p8_b18': "Gallagher Brigand Mk. I (Ящик)",
    'p8_b19': "Silverhand - Mk. IV (Ящик)",
    'p8_b20': "Kivela Power Wheel 80-1 (Ящик)",
    'p8_b21': "King Spire Mk. I (Ящик)",
    'p8_b22': "Drummond 100a (Ящик)",
    'p8_b23': "Rooster - Lamploader (Ящик)",
    'p8_b24': "Rooster - Tumblebox (Ящик)",
    'p8_b25': "Rooster - Junkwagon (Ящик)",
    'p8_b26': "Самосвал Dunne Loadlugger 3c (Ящик)",
    'p8_b27': "Dunne Transport (Ящик)",
    'p8_b28': "81f-f Ronan Blackguard (Ящик)",
    'p8_b29': "74b-1 Ronan Gunship (Ящик)",
    'p8_b30': "Das Krokodil by VAC (Ящик)",
    'p8_b31': "68A-4 Ronan Fathomer (Ящик)",
    'p8_b32': "BMS - Aquatipper (Ящик)",
    'p8_b33': "BMS - Ironship (Ящик)",
    'p8_b34': "Rinnspeir Ornitier-Class Gunship (Ящик)",
    'p8_b35': "Bellweather by VAC (Ящик)",
    # --- page 9 ---
    'p9_b1': "Поддон для материалов (Ящик)",
    'p9_b2': "Контейнер для ресурсов (Ящик)",
    'p9_b3': "Грузовой контейнер (Ящик)",
    'p9_b4': "Leary AA-70 Bolas (Ящик)",
    'p9_b5': "Leary Shellbore 68-мм (Ящик)",
    'p9_b6': "Huber Exalt 150mm (Ящик)",
    'p9_b7': "Leary Snare Trap 20 (Ящик)",
    'p9_b8': "Huber Lariat 120мм (Ящик)",
    'p9_b9': "Бетономешалка (Ящик)",
    'p9_b10': "Construction Equipment (Ящик)",
    'p9_b11': "Жидкостный контейнер (Ящик)",
    # --- page 10 ---
    'p10_b1': "Базовые материалы (Ящик)",
    'p10_b2': "Рафинированные материалы (Ящик)",
    'p10_b3': "Порох (Ящик)",
    'p10_b4': "Тяжёлый порох (Ящик)",
    # --- page 11 ---
    'p11_b1': "Dunne Dousing Engine 3r",
    'p11_b2': "O’Brien V.101 Freeman",
    'p11_b3': "O’Brien v.200 Squire",
    'p11_b4': "O’Brien V.113 Gravekeeper",
    'p11_b5': "O’Brien V.130 Wild Jack",
    'p11_b6': "94.5мм (Ящик)",
    'p11_b7': "228 Satterley Heavy Storm Rifle (Ящик)",
    'p11_b8': "Booker Greyhound Model 910 (Ящик)",
    'p11_b9': "75-мм (Ящик)",
    'p11_b10': "BMS - Fabricator",
    'p11_b11': "Model-7 “Evie” (Ящик)",
    'p11_b12': "Noble Firebrand Mk. XVII",
    'p11_b13': "Нестабильные материалы (Ящик)",
    'p11_b14': "Редкие сплавы (Ящик)",
    'p11_b15': "Balfour Rampart 68-мм",
    'p11_b16': "4C-Зажигательная ракета (Ящик)",
    'p11_b17': "Niska-Rycker Mk. IX Skycaller",
    'p11_b18': "Niska Mk. II Blinder",
    'p11_b19': "Niska Mk. III Scar Twin",
    'p11_b20': "BMS - Scrap Hauler",
    'p11_b21': "Cnute Cliffwrest",
    'p11_b22': "3C-Фугасная ракета (Ящик)",
    'p11_b23': "Crow’s Foot Mine (Ящик)",
    'p11_b24': "Balfour Stockade 75-мм",
    'p11_b25': "Rycker 4/3-F Wasp Nest",
    'p11_b26': "Devitt-Caine Mk. IV MMR",
    'p11_b27': "Devitt Ironhide Mk. IV",
    'p11_b28': "300-мм (Ящик)",
    'p11_b29': "Gallagher Thornfall Mk. VI",
    'p11_b30': "Gallagher Highwayman Mk. III",
    'p11_b31': "Gallagher Outlaw Mk. II",
    'p11_b32': "Silverhand Lordscar - Mk. X",
    'p11_b33': "Silverhand Chieftain - Mk. VI",
    'p11_b34': "King Jester Mk. I-1",
    'p11_b35': "King Gallant Mk. II",
    'p11_b36': "Drummond Spitfire 100d",
    'p11_b37': "Drummond Loscann 55c",
    'p11_b38': "Abisme AT-99 Mine (Ящик)",
    'p11_b39': "Rooster - Lamploader",
    'p11_b40': "Rooster - Tumblebox",
    'p11_b41': "Dunne Leatherback 2a",
    'p11_b42': "Dunne Landrunner 12c",
    'p11_b43': "E680-S Rudder Lock (Ящик)",
    'p11_b44': "Зажигательный минометный снаряд (Ящик)",
    # --- page 12 ---
    'p12_b1': "Tulka I1.9 White Raven",
    'p12_b2': "Luminary Mk. II Harbinger",
    'p12_b3': "M925 Austringer Man-O-War",
    'p12_b4': "Rinnspeir Mk. I Zealot",
    'p12_b5': "Tulka P4 Welkinrive",
    'p12_b6': "Warden Aircraft Mechanical Parts (Small)",
    'p12_b7': "Warden Aircraft Mechanical Parts (Large)",
    'p12_b8': "Warden Aircraft Engine (Small)",
    'p12_b9': "Warden Aircraft Engine (Large)",
    'p12_b10': "Cloudrunner’s Vesture (Ящик)",
    'p12_b11': "Aviator’s Raiment (Ящик)",
    'p12_b12': "Paratrooper’s Ruck (Ящик)",
}

# ----------------- helpers -----------------
def apply_rounded_mask(widget, size: QSize, radius: float = ROUNDED_RADIUS):
    """Apply a smooth rounded mask using QBitmap for better quality."""
    from PyQt5.QtGui import QBitmap, QPainter, QBrush
    from PyQt5.QtCore import Qt
    
    # Create bitmap mask
    mask = QBitmap(size)
    mask.fill(Qt.color0)  # fill with transparent
    
    # Paint rounded rectangle with antialiasing
    painter = QPainter(mask)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    painter.setBrush(QBrush(Qt.color1))  # opaque white
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size.width(), size.height(), radius, radius)
    painter.end()
    
    widget.setMask(mask)


class ImageButton(QPushButton):
    def __init__(self, page, index, image_path=None, parent=None):
        super().__init__(parent)
        self.page = page
        self.index = index
        self.image_path = image_path or ""
        self.pixmap = None
        self.orig_size = QSize(150, 150)

        # Strict fixed size
        self.setFixedSize(BUTTON_SIZE)

        # Тёмный фон для кнопок (иконки остаются видимыми)
        # border-radius визуально; mask гарантирует обрезку содержимого
        self.setStyleSheet(
            "QPushButton {"
            "  background-color: #2b2b2b;"
            "  color: #e6e6e6;"
            "  border: 1px solid #444444;"
            f"  border-radius: {int(ROUNDED_RADIUS)}px;"
            "  padding: 0px;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #1f1f1f;"
            "}"
        )

        self.setText("")

        # Use resource_path to support exe packaging
        if image_path:
            rp = resource_path(image_path)
            if os.path.exists(rp):
                self.load_pixmap(rp)
            else:
                # try original path (fallback), else text label
                if os.path.exists(image_path):
                    self.load_pixmap(image_path)
                else:
                    self.setText(f"B{index}")

        # Apply rounded mask to clip contents (icons) to rounded corners
        apply_rounded_mask(self, BUTTON_SIZE, radius=ROUNDED_RADIUS)

    def load_pixmap(self, path):
        pix = QPixmap(path)
        if not pix.isNull():
            self.pixmap = pix
            self.orig_size = pix.size()
            self.setText("")
            self.update_icon()
        else:
            self.pixmap = None

    def update_icon(self):
        if not self.pixmap:
            return
        # Stretch to whole button (ignore aspect ratio) as requested
        scaled = self.pixmap.scaled(BUTTON_SIZE, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.setIcon(QIcon(scaled))
        self.setIconSize(BUTTON_SIZE)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("написание квоты")
        # set window icon from resource (works in exe if icon.ico added)
        ico_path = resource_path("icon.ico")
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))

        self.resize(1200, 925)

        main_layout = QHBoxLayout(self)

        # Left: pages area (buttons)
        pages_layout = QVBoxLayout()

        # Navigation bar (page buttons) — с иконками
        nav_layout = QHBoxLayout()
        self.page_buttons = []

        PAGE_ICON_PATTERN = "images/page{n}.png"
        PAGE_ICON_MAPPING = {
            0: "images/1.png",
            1: "images/2.png",
            2: "images/3.png",
            3: "images/4.png",
            4: "images/5.png",
            5: "images/6.png",
            6: "images/7.png",
            7: "images/8.png",
            8: "images/9.png",
            9: "images/10.png",
            10: "images/ScoutVehicleOffensiveW.png",
            11: "images/Luminary Mk. II Harbinger.png"
        }

        NAV_ICON_SIZE = QSize(64, 64)
        NAV_BUTTON_SIZE = QSize(64, 64)

        for i in range(len(PAGE_BUTTON_COUNTS)):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.clicked.connect(self.make_goto_page(i))

            # style like ImageButton (same rounded radius)
            btn.setStyleSheet(
                "QPushButton {"
                "  background-color: #2b2b2b;"
                "  color: #e6e6e6;"
                "  border: 1px solid #444444;"
                f"  border-radius: {int(ROUNDED_RADIUS)}px;"
                "  padding: 0px;"
                "}"
                "QPushButton:pressed {"
                "  background-color: #1f1f1f;"
                "}"
            )

            icon_path = PAGE_ICON_MAPPING.get(i, PAGE_ICON_PATTERN.format(n=i+1))
            rp = resource_path(icon_path)
            if os.path.exists(rp):
                pix = QPixmap(rp)
                if not pix.isNull():
                    scaled = pix.scaled(NAV_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    btn.setIcon(QIcon(scaled))
                    btn.setIconSize(scaled.size())
                    btn.setText("")
                    btn.setAccessibleName(str(i+1))
                else:
                    btn.setText(str(i+1))
            else:
                if os.path.exists(icon_path):
                    pix = QPixmap(icon_path)
                    if not pix.isNull():
                        scaled = pix.scaled(NAV_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        btn.setIcon(QIcon(scaled))
                        btn.setIconSize(scaled.size())
                        btn.setText("")
                        btn.setAccessibleName(str(i+1))
                    else:
                        btn.setText(str(i+1))
                else:
                    btn.setText(str(i+1))

            btn.setFixedSize(NAV_BUTTON_SIZE)

            # Apply mask for exact rounded clipping
            apply_rounded_mask(btn, NAV_BUTTON_SIZE, radius=ROUNDED_RADIUS)

            nav_layout.addWidget(btn)
            self.page_buttons.append(btn)

        pages_layout.addLayout(nav_layout)

        # Stacked widget with pages inside a scroll area
        self.stacked = QStackedWidget()
        self.page_widgets = []
        self.all_image_buttons = []  # flat list for updates

        for p, count in enumerate(PAGE_BUTTON_COUNTS, start=1):
            # For page 11 (p==11) create internal scroll area because many buttons
            if p in (8, 11):
                inner_widget = QWidget()
                grid = QGridLayout()
                grid.setSpacing(BUTTON_SPACING)
                grid.setContentsMargins(10, 10, 10, 10)
                grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

                columns = COLUMNS
                rows = ceil(count / columns)

                page_buttons = []
                for idx in range(1, count + 1):
                    key = f"p{p}_b{idx}"
                    path = IMAGE_MAPPING.get(key, IMAGE_PATH_PATTERN.format(page=p, idx=idx))
                    btn = ImageButton(page=p, index=idx, image_path=path)
                    btn.clicked.connect(self.button_clicked)
                    page_buttons.append(btn)
                    self.all_image_buttons.append(btn)

                # place buttons into grid
                k = 0
                for r in range(rows):
                    for c in range(columns):
                        if k >= len(page_buttons):
                            break
                        grid.addWidget(page_buttons[k], r, c)
                        k += 1

                for r in range(rows):
                    grid.setRowStretch(r, 0)
                grid.setRowStretch(rows, 1)
                for c in range(columns):
                    grid.setColumnStretch(c, 0)

                inner_widget.setLayout(grid)
                # Белый фон — только для последней страницы (p11)
                if p == 11:
                    inner_widget.setStyleSheet("background-color: #ffffff;")

                # create scroll area for this page
                page_scroll = QScrollArea()
                page_scroll.setWidgetResizable(True)
                page_scroll.setWidget(inner_widget)
# Белый viewport — только для последней страницы (p11)
                if p == 11:
                    page_scroll.viewport().setStyleSheet("background-color: #ffffff;")
                # show scrollbars as needed
                page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

                self.stacked.addWidget(page_scroll)
                self.page_widgets.append(page_scroll)
            else:
                page_widget = QWidget()
                grid = QGridLayout()
                grid.setSpacing(BUTTON_SPACING)
                grid.setContentsMargins(10, 10, 10, 10)
                grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

                columns = COLUMNS
                rows = ceil(count / columns)

                page_buttons = []
                for idx in range(1, count + 1):
                    key = f"p{p}_b{idx}"
                    path = IMAGE_MAPPING.get(key, IMAGE_PATH_PATTERN.format(page=p, idx=idx))
                    btn = ImageButton(page=p, index=idx, image_path=path)
                    btn.clicked.connect(self.button_clicked)
                    page_buttons.append(btn)
                    self.all_image_buttons.append(btn)

                k = 0
                for r in range(rows):
                    for c in range(columns):
                        if k >= len(page_buttons):
                            break
                        grid.addWidget(page_buttons[k], r, c)
                        k += 1

                for r in range(rows):
                    grid.setRowStretch(r, 0)
                grid.setRowStretch(rows, 1)
                for c in range(columns):
                    grid.setColumnStretch(c, 0)

                page_widget.setLayout(grid)
                self.stacked.addWidget(page_widget)
                self.page_widgets.append(page_widget)

        # put stacked into scroll area so many buttons fit; this keeps content top-left
        outer_scroll = QScrollArea()
        outer_scroll.setWidgetResizable(False)  # do not allow widget to resize to viewport
        outer_scroll.setWidget(self.stacked)

        # Layout parameters for fixed box (same as до этого) with EXTRA_WIDTH
        visible_rows = 5
        visible_cols = COLUMNS  # 6

        margin = 10  # padding on each side
        spacing = BUTTON_SPACING

        total_width = (
            visible_cols * BUTTON_SIZE.width()
            + (visible_cols - 1) * spacing
            + 2 * margin
            + EXTRA_WIDTH
        )
        total_height = visible_rows * BUTTON_SIZE.height() + (visible_rows - 1) * spacing + 2 * margin

        self.stacked.setFixedSize(total_width, total_height)
        outer_scroll.setFixedSize(total_width + 2, total_height + 2)  # +2 for frame/border safety

        # outer scrollbars hidden (inner page 11 has its own scroll area)
        outer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        pages_layout.addWidget(outer_scroll)


        # Right: notes textbox + quantity input
        right_layout = QVBoxLayout()
        right_label = QLabel("Квота:")
        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Здесь будут записи...")
        self.notes.setMinimumWidth(520)

        qty_layout = QHBoxLayout()
        qty_label = QLabel("Кол-во:")
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 999999)
        self.qty_spin.setValue(1)
        self.qty_spin.setToolTip("Выберите количество ящиков, которое будет добавлено при нажатии на кнопку")
        self.qty_spin.setButtonSymbols(QSpinBox.NoButtons)
        # Прямые стили на конкретные поля — чтобы перебить любые глобальные настройки
        self.notes.setStyleSheet("""
            QTextEdit {
                border: 3px solid #000;
                border-radius: 12px;
                padding: 10px;
                background: #ffffff;
                color: #071422;
            }
        """)
        self.qty_spin.setStyleSheet("""
            QSpinBox {
                border: 3px solid #000;
                border-radius: 8px;
                padding: 6px 12px;
                background: #ffffff;
                color: #071422;
                min-width: 80px;
            }
        """)
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_spin)

        right_layout.addLayout(qty_layout)
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.notes)

        main_layout.addLayout(pages_layout)
        main_layout.addLayout(right_layout)
        main_layout.setStretch(0, 4)
        main_layout.setStretch(1, 1)

        # select first page
        self.goto_page(0)

    def make_goto_page(self, index):
        def fn():
            self.goto_page(index)
        return fn

    def goto_page(self, index):
        self.stacked.setCurrentIndex(index)
        for i, b in enumerate(self.page_buttons):
            b.setChecked(i == index)
        # update icons
        self.update_all_icons()

    def button_clicked(self):
        btn = self.sender()
        key = f"p{btn.page}_b{btn.index}"
        name = ITEM_TEXT.get(key)
        n = int(self.qty_spin.value())
        if name:
            line = f"{name},{n}"
        else:
            if btn.image_path:
                rp = resource_path(btn.image_path)
                if os.path.exists(rp):
                    line = f"{os.path.basename(rp)},{n}"
                else:
                    line = f"{os.path.basename(btn.image_path)},{n}"
            else:
                line = f"B{btn.index},{n}"
        self.notes.append(line)
        print(line)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # keep icons updated
        self.update_all_icons()

    def update_all_icons(self):
        for btn in self.all_image_buttons:
            btn.update_icon()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Set requested font (optional)
    app.setFont(QFont("Inter", 10))

        # Глобальный стиль для текстовых полей и плашек — как в сплиттере/сканере
    app.setStyleSheet("""
            QLabel {
                color: #071422;
                background: transparent;
                border: none;
            }
            QTextEdit, QPlainTextEdit {
                border: 3px solid #000;
                border-radius: 12px;
                padding: 10px;
                background: #ffffff;
                color: #071422;
            }
            QTextEdit:focus, QPlainTextEdit:focus {
                border: 3px solid #000;
                background: #ffffff;
            }
            QSpinBox {
                border: 3px solid #000;
                border-radius: 8px;
                padding: 6px 8px;
                background: #ffffff;
                color: #071422;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px;
                border: none;
            }
        """)

    # set app icon (works both in dev and in exe if icon present)
    app_icon_path = resource_path("icon.ico")
    if os.path.exists(app_icon_path):
        app.setWindowIcon(QIcon(app_icon_path))

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

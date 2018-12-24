#!/usr/bin/env python
import json

from biomes import BIOMES
from enum import Enum

BIOMES["tropical_beach"] = [
    "biomesoplenty:oasis",
    "biomesoplenty:white_beach",
    "biomesoplenty:tropical_island",
]

RARITY = {
    "cultivated": 25,
    "common": 35,
    "uncommon": 50,
    "rare": 60,
}

KIND_MULTIPLIER = {
    "fruit": 0.8,
    "nut": 1.0,
    "spice": 1.2,
    "item": 1.3,
}

class Tree(object):

    def __init__(self, name, kind, rarity, *climates, enabled=True):
        self.name = name
        self.climates = climates
        self.enabled = enabled
        self.kind = kind
        self.rarity = rarity

    def __str__(self):
        biomes = []
        for climate in self.climates:
            for biome in BIOMES[climate]:
                biomes.append(biome)

        result = []
        result.append(self.name + " {")
        result.append("    B:enableGeneration=" + ("true" if self.enabled else "false"))
        result.append("    I:rarity=" + str(RARITY[self.rarity] * KIND_MULTIPLIER[self.kind]))
        result.append("    S:whitelist <")
        for biome in biomes:
            result.append("        " + biome)
        result.append("    >")
        result.append("}")
        return "\n".join(result)


TREES = [
    Tree("apple", "fruit", "cultivated", "hills", "temperate_forest"),
    Tree("apricot", "fruit", "common", "hills", "temperate_forest"),
    Tree("avocado", "fruit", "cultivated", "warm_forest", "tropical"),
    Tree("banana", "fruit", "cultivated", "tropical"),
    Tree("breadfruit", "fruit", "uncommon", "tropical"),
    Tree("dragonfruit", "fruit", "common", "tropical"),
    Tree("durian", "fruit", "rare", "tropical"),
    Tree("fig", "fruit", "common", "arid"),
    Tree("gooseberry", "fruit", "uncommon", "cold_forest", "hills", "temperate_forest"),
    Tree("grapefruit", "fruit", "uncommon", "arid", "warm_forest", "tropical"),
    Tree("guava", "fruit", "cultivated", "tropical"),
    Tree("jackfruit", "fruit", "common", "arid"),
    Tree("lemon", "fruit", "common", "arid", "warm_forest"),
    Tree("lime", "fruit", "common", "arid", "warm_forest"),
    Tree("lychee", "fruit", "uncommon", "tropical"),
    Tree("mango", "fruit", "cultivated", "arid", "warm_forest", "tropical"),
    Tree("olive", "fruit", "cultivated", "arid", "warm_forest"),
    Tree("orange", "fruit", "cultivated", "arid", "warm_forest"),
    Tree("papaya", "fruit", "common", "tropical"),
    Tree("passionfruit", "fruit", "uncommon", "hills", "temperate_forest", "warm_forest", "tropical"),
    Tree("pawpaw", "fruit", "rare", "hills", "temperate_forest"),
    Tree("peach", "fruit", "uncommon", "hills", "temperate_forest"),
    Tree("pear", "fruit", "common", "cold_forest", "hills", "temperate_forest"),
    Tree("persimmon", "fruit", "uncommon", "cold_forest", "hills", "temperate_forest"),
    Tree("plum", "fruit", "uncommon", "hills", "temperate_forest"),
    Tree("pomegranate", "fruit", "uncommon", "arid"),
    Tree("rambutan", "fruit", "uncommon", "tropical"),
    Tree("soursop", "fruit", "uncommon", "tropical"),
    Tree("starfruit", "fruit", "rare", "tropical"),

    Tree("almond", "nut", "cultivated", "arid"),
    Tree("cashew", "nut", "uncommon", "tropical"),
    Tree("chestnut", "nut", "common", "hills", "temperate_forest"),
    Tree("coconut", "nut", "common", "tropical_beach"),
    Tree("hazelnut", "nut", "rare", "temperate_forest"),
    Tree("pecan", "nut", "uncommon", "temperate_forest", "warm_forest"),
    Tree("pistachio", "nut", "uncommon", "arid", "desert", "mesa"),
    Tree("walnut", "nut", "cultivated", "cold_forest", "hills", "temperate_forest"),

    Tree("cinnamon", "spice", "rare", "tropical"),
    Tree("maple", "spice", "common", "cold_forest", "temperate_forest"),
    Tree("nutmeg", "spice", "common", "warm_forest", "tropical"),
    Tree("peppercorn", "spice", "uncommon", "arid", "tropical"),
    Tree("tamarind", "spice", "common", "arid", "tropical"),
    Tree("vanillabean", "spice", "rare", "warm_forest", "tropical"),

    Tree("paperbark", "item", "uncommon", "arid"),
    Tree("spiderweb", "item", "rare", "tropical"),
]

for tree in TREES:
    if tree.kind == "item":
        tree.enabled = False

print("_common_fruit_trees {")
print("    B:enableFruitTreeGeneration=true")
print("    I:fruitGrowthSpeed=25")
print("}")
print("")
print("\n\n".join(str(tree) for tree in TREES))

#!/usr/bin/env python
import json
import hashlib

from .biomes import BIOMES
from enum import Enum

class Altitude(Enum):
    LAVA = (0, 12)
    DEEP = (13, 48)
    BURIED = (49, 64)
    SURFACE = (65, 80)
    HILLS = (81, 128)
    MOUNTAINS = (128, 256)

    NETHER_OCEAN = (0, 32)
    NETHER_LOWER = (32, 80)
    NETHER_UPPER = (80, 128)

    def __init__(self, min_height=0, max_height=256):
        self.min_height = min_height
        self.max_height = max_height


class Density(Enum):
    DENSE = (12, 12)
    NORMAL = (8, 9)
    RARE = (4, 12)
    TRACE = (2, 6)

    def __init__(self, cluster_size=0, cluster_count=0, chunk_chance=1):
        self.cluster_size = cluster_size
        self.cluster_count = cluster_count
        self.chunk_chance = chunk_chance

    def adjusted_cluster_count(self, altitude):
        altitude_factor = (altitude.max_height - altitude.min_height) / 16
        return round(altitude_factor * self.cluster_count)


class Ore(object):

    def __init__(self, name=None, metadata=0, weight=100):
        self.name = name
        self.metadata = metadata
        self.weight = weight

    def as_json(self):
        if self.metadata == 0 and self.weight == 100:
            return self.name
        else:
            result = {"name": self.name}

            if self.metadata != 0:
                result["metadata"] = self.metadata
            if self.weight != 100:
                result["weight"] = self.weight

            return result

    def weighted(self, weight):
        return Ore(self.name, self.metadata, weight)


class Vein(object):

    def __init__(self, name=None, *ores):
        self.name = name
        self.ores = ores

    def as_json(self):
        if len(self.ores) == 1:
            return self.ores[0].as_json()
        else:
            return list(o.as_json() for o in self.ores)


class Deposit(object):

    _next_id = 1

    def __init__(self, vein, altitude, density, *biome_groups, dimension=0):
        self.vein = vein
        self.altitude = altitude
        self.biomes = []
        self.density = density
        self.dimension = dimension

        self.id = Deposit._next_id
        Deposit._next_id += 1

        if dimension == -1:
            self.material = Vein("netherrack", Ore("netherrack", -1))
        else:
            self.material = Vein("stone", Ore("stone", -1))

        for biome_group in biome_groups:
            for biome in BIOMES[biome_group]:
                self.biomes.append(biome)

        self.biomes = sorted(set(self.biomes))
        hasher = hashlib.new("md5")
        for biome in self.biomes:
            hasher.update(biome.encode("UTF-8"))
        self.id = hasher.hexdigest()


    @property
    def name(self):
        return f"{self.vein.name.upper()}-{self.altitude.name}-{self.id}"

    def as_json(self):
        result = {
            "enabled": True,
            "generator": {
                "block": self.vein.as_json(),
                "material": self.material.as_json(),
                "type": "cluster",
                "cluster-size": self.density.cluster_size,
            },
            "chunk-chance": self.density.chunk_chance,
            "cluster-count": self.density.adjusted_cluster_count(self.altitude),

            "distribution": "uniform",
            "min-height": self.altitude.min_height,
            "max-height": self.altitude.max_height,

            "biome": {
                "restriction": "whitelist",
                "value": {
                    "type": "id",
                    "entry": self.biomes,
                }
            },
            "dimension": {
                "restriction": "blacklist",
                "value": [ -1, 1 ]
            }
        }

        if self.dimension != 0:
            result["dimension"] = {
                "restriction": "whitelist",
                "value": [ self.dimension ],
            }

        return result


class GravelDeposit(Deposit):

    def __init__(self, vein, density=Density.NORMAL, *biome_groups):
        super().__init__(vein, Altitude.SURFACE, density, *biome_groups)

    def as_json(self):
        result = super().as_json()
        result["generator"]["material"] = [ "gravel" ]
        result["cluster-count"] *= 2
        result["min-height"] = 0
        result["max-height"] = 70
        return result

# Ore Definitions ######################################################################################################

# Gravel
gravel = Ore("minecraft:gravel")
tin_gravel = Ore("gravelores:tin_gravel_ore")
gold_gravel = Ore("gravelores:gold_gravel_ore")
iron_gravel = Ore("gravelores:iron_gravel_ore")

# Metals
aluminum_ore = Ore("modernmetals:aluminum_ore")
ardite_ore = Ore("tconstruct:ore", 1)
cobalt_ore = Ore("tconstruct:ore")
copper_ore = Ore("basemetals:copper_ore")
gold_ore = Ore("minecraft:gold_ore")
iron_ore = Ore("minecraft:iron_ore")
lead_ore = Ore("basemetals:lead_ore")
nickel_ore = Ore("basemetals:nickel_ore")
platinum_ore = Ore("basemetals:platinum_ore")
silver_ore = Ore("basemetals:silver_ore")
tin_ore = Ore("basemetals:tin_ore")
tungsten_ore = Ore("modernmetals:tungsten_ore")
uranium_ore = Ore("modernmetals:uranium_ore")

# Minerals
apatite_ore = Ore("forestry:resources")
coal_ore = Ore("minecraft:coal_ore")
diamond_ore = Ore("minecraft:diamond_ore")
emerald_ore = Ore("minecraft:emerald_ore")
lapis_ore = Ore("minecraft:lapis_ore")
quartz_ore = Ore("minecraft:quartz_ore")
redstone_ore = Ore("minecraft:redstone_ore")
salt_ore = Ore("baseminerals:salt_ore")
saltpeter_ore = Ore("baseminerals:saltpeter_ore")
sulfur_ore = Ore("baseminerals:sulfur_ore")

# Stone
stone = Ore("minecraft:stone")
netherrack = Ore("minecraft:netherrack")
sandstone = Ore("minecraft:sandstone")

# Overworld Veins
apatite_vein = Vein("apatite", apatite_ore.weighted(99), uranium_ore.weighted(1))
bauxite_vein = Vein("bauxite", aluminum_ore.weighted(100))
coal_vein = Vein("coal", coal_ore.weighted(96), diamond_ore.weighted(2), emerald_ore.weighted(2))
copper_vein = Vein("copper", copper_ore.weighted(68), redstone_ore.weighted(26), gold_ore.weighted(6))
diamond_vein = Vein("diamond", coal_ore.weighted(60), diamond_ore.weighted(20), emerald_ore.weighted(20))
galena_vein = Vein("galena", silver_ore.weighted(50), lead_ore.weighted(50))
gold_vein = Vein("gold", gold_ore.weighted(68), copper_ore.weighted(26), nickel_ore.weighted(6))
iron_vein = Vein("iron", iron_ore.weighted(53), nickel_ore.weighted(26), tin_ore.weighted(21))
lapis_vein = Vein("lapis", lapis_ore.weighted(68), iron_ore.weighted(28), sulfur_ore.weighted(4))
lead_vein = Vein("lead", lead_ore.weighted(58), silver_ore.weighted(42))
magnetite_vein = Vein("magnetite", iron_ore.weighted(85), gold_ore.weighted(15))
nickel_vein = Vein("nickel", nickel_ore.weighted(90), platinum_ore.weighted(5), iron_ore.weighted(5))
pyrite_vein = Vein("pyrite", iron_ore.weighted(85), sulfur_ore.weighted(15))
redstone_vein = Vein("redstone", redstone_ore.weighted(60), copper_ore.weighted(35), gold_ore.weighted(5))
saltpeter_vein = Vein("saltpeter", sandstone.weighted(60), saltpeter_ore.weighted(40))
silver_vein = Vein("silver", silver_ore.weighted(58), lead_ore.weighted(42))
tungsten_vein = Vein("tungsten", tungsten_ore.weighted(100))
uranium_vein = Vein("uranium", uranium_ore.weighted(65), lead_ore.weighted(35))

# Nether Veins
ardite_vein = Vein("ardite", netherrack.weighted(50), ardite_ore.weighted(50))
cobalt_vein = Vein("ardite", netherrack.weighted(70), cobalt_ore.weighted(30))
quartzite_vein = Vein("quartzite", quartz_ore.weighted(60), netherrack.weighted(40))
sulfur_vein = Vein("sulfur", sulfur_ore.weighted(50), stone.weighted(50))

# Gravel Veins
gold_gravel_vein = Vein("gold_gravel", gravel.weighted(95), gold_gravel.weighted(5))
tin_gravel_vein = Vein("tin_gravel", gravel.weighted(50), tin_gravel.weighted(50))
iron_gravel_vein = Vein("iron_gravel", gravel.weighted(70), tin_gravel.weighted(30))


# Full Data Structure ##################################################################################################


data = {
    "populate": {d.name: d.as_json() for d in [
        # arid
        Deposit(bauxite_vein, Altitude.BURIED, Density.TRACE, "arid"),
        Deposit(bauxite_vein, Altitude.SURFACE, Density.RARE, "arid"),
        Deposit(bauxite_vein, Altitude.HILLS, Density.NORMAL, "arid"),
        Deposit(bauxite_vein, Altitude.MOUNTAINS, Density.TRACE, "arid"),

        Deposit(magnetite_vein, Altitude.LAVA, Density.DENSE, "arid"),
        Deposit(magnetite_vein, Altitude.DEEP, Density.NORMAL, "arid"),
        Deposit(magnetite_vein, Altitude.BURIED, Density.RARE, "arid"),
        Deposit(magnetite_vein, Altitude.SURFACE, Density.TRACE, "arid"),

        GravelDeposit(tin_gravel_vein, Density.NORMAL, "arid"),

        # cold desert
        Deposit(lead_vein, Altitude.DEEP, Density.NORMAL, "cold_desert"),
        Deposit(lead_vein, Altitude.BURIED, Density.RARE, "cold_desert"),
        Deposit(galena_vein, Altitude.SURFACE, Density.TRACE, "cold_desert"),
        Deposit(galena_vein, Altitude.HILLS, Density.RARE, "cold_desert"),
        Deposit(silver_vein, Altitude.MOUNTAINS, Density.NORMAL, "cold_desert"),

        GravelDeposit(tin_gravel_vein, Density.NORMAL, "cold_desert"),

        # cold forest
        Deposit(apatite_vein, Altitude.BURIED, Density.NORMAL, "cold_forest"),
        Deposit(apatite_vein, Altitude.SURFACE, Density.RARE, "cold_forest"),

        Deposit(lead_vein, Altitude.DEEP, Density.NORMAL, "cold_forest"),
        Deposit(lead_vein, Altitude.BURIED, Density.RARE, "cold_forest"),
        Deposit(galena_vein, Altitude.SURFACE, Density.TRACE, "cold_forest"),
        Deposit(galena_vein, Altitude.HILLS, Density.RARE, "cold_forest"),
        Deposit(galena_vein, Altitude.MOUNTAINS, Density.NORMAL, "cold_forest"),

        # desert
        Deposit(saltpeter_vein, Altitude.BURIED, Density.NORMAL, "desert"),
        Deposit(saltpeter_vein, Altitude.SURFACE, Density.RARE, "desert"),

        # frozen
        Deposit(silver_vein, Altitude.SURFACE, Density.TRACE, "frozen"),
        Deposit(silver_vein, Altitude.HILLS, Density.RARE, "frozen"),
        Deposit(silver_vein, Altitude.MOUNTAINS, Density.NORMAL, "frozen"),

        # hills
        Deposit(coal_vein, Altitude.DEEP, Density.RARE, "hills"),
        Deposit(coal_vein, Altitude.BURIED, Density.NORMAL, "hills"),
        Deposit(coal_vein, Altitude.SURFACE, Density.NORMAL, "hills"),
        Deposit(coal_vein, Altitude.HILLS, Density.NORMAL, "hills"),
        Deposit(coal_vein, Altitude.MOUNTAINS, Density.RARE, "hills"),

        Deposit(iron_vein, Altitude.LAVA, Density.DENSE, "hills"),
        Deposit(iron_vein, Altitude.DEEP, Density.DENSE, "hills"),
        Deposit(iron_vein, Altitude.BURIED, Density.NORMAL, "hills"),
        Deposit(iron_vein, Altitude.SURFACE, Density.RARE, "hills"),
        Deposit(iron_vein, Altitude.HILLS, Density.NORMAL, "hills"),
        Deposit(iron_vein, Altitude.MOUNTAINS, Density.NORMAL, "hills"),

        # mesa
        Deposit(gold_vein, Altitude.LAVA, Density.DENSE, "mesa"),
        Deposit(gold_vein, Altitude.DEEP, Density.NORMAL, "mesa"),
        Deposit(gold_vein, Altitude.BURIED, Density.RARE, "mesa"),
        Deposit(magnetite_vein, Altitude.SURFACE, Density.TRACE, "mesa"),
        Deposit(magnetite_vein, Altitude.HILLS, Density.RARE, "mesa"),
        Deposit(magnetite_vein, Altitude.MOUNTAINS, Density.NORMAL, "mesa"),

        # mountains
        Deposit(diamond_vein, Altitude.LAVA, Density.NORMAL, "mountains"),
        Deposit(diamond_vein, Altitude.DEEP, Density.RARE, "mountains"),
        Deposit(diamond_vein, Altitude.BURIED, Density.TRACE, "mountains"),

        Deposit(iron_vein, Altitude.LAVA, Density.DENSE, "mountains"),
        Deposit(iron_vein, Altitude.DEEP, Density.DENSE, "mountains"),
        Deposit(iron_vein, Altitude.BURIED, Density.NORMAL, "mountains"),
        Deposit(iron_vein, Altitude.SURFACE, Density.RARE, "mountains"),
        Deposit(iron_vein, Altitude.HILLS, Density.NORMAL, "mountains"),
        Deposit(iron_vein, Altitude.MOUNTAINS, Density.NORMAL, "mountains"),

        Deposit(tungsten_vein, Altitude.LAVA, Density.NORMAL, "mountains"),

        # nether
        Deposit(ardite_vein, Altitude.NETHER_LOWER, Density.RARE, "nether", dimension=-1),
        Deposit(ardite_vein, Altitude.NETHER_UPPER, Density.TRACE, "nether", dimension=-1),

        Deposit(cobalt_vein, Altitude.NETHER_LOWER, Density.TRACE, "nether", dimension=-1),
        Deposit(cobalt_vein, Altitude.NETHER_UPPER, Density.RARE, "nether", dimension=-1),

        Deposit(quartzite_vein, Altitude.NETHER_OCEAN, Density.DENSE, "nether", dimension=-1),
        Deposit(quartzite_vein, Altitude.NETHER_LOWER, Density.NORMAL, "nether", dimension=-1),
        Deposit(quartzite_vein, Altitude.NETHER_UPPER, Density.RARE, "nether", dimension=-1),

        # ocean
        Deposit(lapis_vein, Altitude.LAVA, Density.RARE, "ocean"),
        Deposit(lapis_vein, Altitude.DEEP, Density.RARE, "ocean"),
        Deposit(lapis_vein, Altitude.BURIED, Density.TRACE, "ocean"),
        Deposit(lapis_vein, Altitude.SURFACE, Density.TRACE, "ocean"),

        GravelDeposit(tin_gravel_vein, Density.DENSE, "ocean"),
        GravelDeposit(iron_gravel_vein, Density.DENSE, "ocean"),

        # plains
        Deposit(redstone_vein, Altitude.LAVA, Density.NORMAL, "plains"),
        Deposit(copper_vein, Altitude.DEEP, Density.DENSE, "plains"),
        Deposit(copper_vein, Altitude.BURIED, Density.NORMAL, "plains"),
        Deposit(copper_vein, Altitude.SURFACE, Density.RARE, "plains"),

        # shore
        Deposit(lapis_vein, Altitude.LAVA, Density.NORMAL, "shore"),
        Deposit(lapis_vein, Altitude.DEEP, Density.NORMAL, "shore"),
        Deposit(lapis_vein, Altitude.BURIED, Density.RARE, "shore"),
        Deposit(lapis_vein, Altitude.SURFACE, Density.TRACE, "shore"),

        GravelDeposit(gold_gravel_vein, Density.TRACE, "shore"),
        GravelDeposit(iron_gravel_vein, Density.RARE, "shore"),
        GravelDeposit(tin_gravel_vein, Density.NORMAL, "shore"),

        # swamp
        Deposit(coal_vein, Altitude.DEEP, Density.NORMAL, "swamp"),
        Deposit(coal_vein, Altitude.BURIED, Density.DENSE, "swamp"),
        Deposit(coal_vein, Altitude.SURFACE, Density.TRACE, "swamp"),

        # temperate forest
        Deposit(apatite_vein, Altitude.BURIED, Density.NORMAL, "temperate_forest"),
        Deposit(apatite_vein, Altitude.SURFACE, Density.RARE, "temperate_forest"),

        Deposit(iron_vein, Altitude.LAVA, Density.NORMAL, "overworld"),
        Deposit(iron_vein, Altitude.DEEP, Density.NORMAL, "overworld"),
        Deposit(iron_vein, Altitude.BURIED, Density.RARE, "overworld"),
        Deposit(iron_vein, Altitude.HILLS, Density.RARE, "overworld"),
        Deposit(iron_vein, Altitude.MOUNTAINS, Density.NORMAL, "overworld"),

        # tropical
        Deposit(bauxite_vein, Altitude.SURFACE, Density.NORMAL, "tropical"),

        # warm forest
        Deposit(apatite_vein, Altitude.BURIED, Density.NORMAL, "warm_forest"),
        Deposit(apatite_vein, Altitude.SURFACE, Density.RARE, "warm_forest"),

        # wasteland
        Deposit(uranium_vein, Altitude.LAVA, Density.NORMAL, "wasteland"),
        Deposit(uranium_vein, Altitude.DEEP, Density.RARE, "wasteland"),
        Deposit(lead_vein, Altitude.DEEP, Density.NORMAL, "wasteland"),
        Deposit(lead_vein, Altitude.BURIED, Density.RARE, "wasteland"),
        Deposit(lead_vein, Altitude.SURFACE, Density.TRACE, "wasteland"),

        # overworld
        Deposit(coal_vein, Altitude.DEEP, Density.TRACE, "overworld"),
        Deposit(coal_vein, Altitude.BURIED, Density.RARE, "overworld"),
        Deposit(coal_vein, Altitude.SURFACE, Density.RARE, "overworld"),
        Deposit(coal_vein, Altitude.HILLS, Density.NORMAL, "overworld"),
        Deposit(coal_vein, Altitude.MOUNTAINS, Density.NORMAL, "overworld"),

        Deposit(diamond_vein, Altitude.LAVA, Density.TRACE, "overworld"),

        Deposit(iron_vein, Altitude.LAVA, Density.RARE, "overworld"),
        Deposit(iron_vein, Altitude.DEEP, Density.RARE, "overworld"),
        Deposit(iron_vein, Altitude.BURIED, Density.TRACE, "overworld"),
        Deposit(iron_vein, Altitude.HILLS, Density.TRACE, "overworld"),
        Deposit(iron_vein, Altitude.MOUNTAINS, Density.RARE, "overworld"),

        Deposit(nickel_vein, Altitude.LAVA, Density.RARE, "overworld"),
        Deposit(pyrite_vein, Altitude.LAVA, Density.RARE, "overworld"),
        Deposit(sulfur_vein, Altitude.LAVA, Density.NORMAL, "overworld"),
    ]}
}

print(json.dumps(data, indent=4))

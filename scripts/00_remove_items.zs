import crafttweaker.item.IItemDefinition;
import crafttweaker.item.IItemStack;
import mods.jei.JEI.removeAndHide;

function removeAll(itemStack as IItemStack, metadata as int[]) {
    for index in metadata {
        removeAndHide(itemStack.definition.makeStack(index));
    }
}

function removeInRange(itemStack as IItemStack, start as int, end as int) {
    for i in start..end {
        removeAndHide(itemStack.definition.makeStack(i));
    }
}

print("Removing banned items...");

removeAndHide(<agricraft:debugger>);
removeAndHide(<agricraft:peripheral>);
removeAndHide(<baubles:ring>);
removeAndHide(<biomesoplenty:biome_finder>);
removeAndHide(<forestry:analyzer>);
removeAndHide(<forestry:genetic_filter>);
removeAndHide(<forestry:rainmaker>);
removeAndHide(<genetics:adv_machine>);
removeAndHide(<harvestcraft:apiary>);
removeAndHide(<harvestcraft:market>);
removeAndHide(<malisisdoors:forcefielditem>);
removeAndHide(<minecraft:barrier>);
removeAndHide(<minecraft:beacon>);
removeAndHide(<minecraft:brewing_stand>);
removeAndHide(<minecraft:chain_command_block>);
removeAndHide(<minecraft:command_block>);
removeAndHide(<minecraft:command_block_minecart>);
removeAndHide(<minecraft:enchanting_table>);
removeAndHide(<minecraft:enchanted_book>);
removeAndHide(<minecraft:end_portal_frame>);
removeAndHide(<minecraft:ender_chest>);
removeAndHide(<minecraft:experience_bottle>);
removeAndHide(<minecraft:knowledge_book>);
removeAndHide(<minecraft:repeating_command_block>);
removeAndHide(<minecraft:structure_block>);
removeAndHide(<minecraft:structure_void>);
removeAndHide(<minecraft:totem_of_undying>);
removeAndHide(<twilightforest:ore_meter>);

removeAll(<tconstruct:slime_boots>, [ 0, 1, 2, 4 ]);
removeInRange(<davincisvessels:balloon>, 0, 15);
removeInRange(<genetics:lab_machine>, 0, 4);
removeInRange(<genetics:machine>, 0, 3);
removeInRange(<tconstruct:slimesling>, 0, 4);

print("Done.");

val hammer = <immersiveengineering:tool:0>.reuse();

recipes.addShapeless(<rtfm:book_manual>, [<minecraft:book>,<minecraft:book>]);

recipes.addShaped(<justcoins:copper_coin>, [[<ore:nuggetCopper>, <ore:nuggetCopper>, <ore:nuggetCopper>],[<ore:nuggetCopper>, null, <ore:nuggetCopper>], [<ore:nuggetCopper>, <ore:nuggetCopper>, <ore:nuggetCopper>]]);
recipes.addShaped(<justcoins:silver_coin>, [[<ore:nuggetCopper>, <ore:nuggetCopper>, <ore:nuggetCopper>],[<ore:nuggetCopper>, null, <ore:nuggetCopper>], [<ore:nuggetCopper>, <ore:nuggetCopper>, <ore:nuggetCopper>]]);
recipes.addShaped(<justcoins:gold_coin>, [[<ore:nuggetCopper>, <ore:nuggetCopper>, <ore:nuggetCopper>],[<ore:nuggetCopper>, null, <ore:nuggetCopper>], [<ore:nuggetCopper>, <ore:nuggetCopper>, <ore:nuggetCopper>]]);

recipes.addShaped(<wearablebackpacks:backpack>, [[<ore:leather>, <ore:ingotBronze>, <minecraft:leather>],[<minecraft:leather>, <ore:blockWool>, <minecraft:leather>], [<minecraft:leather>, <minecraft:leather>, <minecraft:leather>]]);
recipes.addShaped(<wearablebackpacks:backpack>, [[<ore:leather>, <ore:ingotCopper>, <minecraft:leather>],[<minecraft:leather>, <ore:blockWool>, <minecraft:leather>], [<minecraft:leather>, <minecraft:leather>, <minecraft:leather>]]);

recipes.remove(<chickenchunks:chunk_loader>);
recipes.addShaped(<chickenchunks:chunk_loader>, [[null, <minecraft:ender_eye>, null],[<minecraft:diamond>, <minecraft:gold_ingot>, <minecraft:diamond>], [<minecraft:gold_ingot>, <minecraft:obsidian>, <minecraft:gold_ingot>]]);

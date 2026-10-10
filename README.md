# Custom Legendary Modifications Remade

Source repository for **Custom Legendary Modifications Remade** (CLM), a Fallout 4 mod by Deadmansprice,
originally released in 2016-2017 on [Nexus Mods](https://www.nexusmods.com/fallout4/mods/5565) and Bethesda.net
(PC, Xbox One and PS4).

CLM adds hundreds of craftable legendary weapon and armor modifications, with a holotape configuration menu
that controls which categories show up at the workbench (free or costly recipes, perk variants, spawning,
variants, balanced or OP).

## Layout

- `docs/DESIGN.md` - how the mod works: naming, the configuration system, and techniques learned building it.
- `data/` - everything that ships, laid out like the game's `Data` folder: the plugin plus the loose files that get
  packed into `Custom Legendary Modifications Remade - Main.ba2` (scripts, facegen mesh) and `- Textures.ba2`.

## History

The first commit is the **1.09 release exactly as shipped in 2017**. Every later change is its own commit, so the
history doubles as a changelog of the 2.0 overhaul.

## Requirements

Fallout 4 with **all six DLC**: Automatron, Far Harbor, Nuka-World, Wasteland Workshop, Contraptions Workshop and
Vault-Tec Workshop. The plugin lists every one of them as a master.

## License

[CC BY 4.0](LICENSE): use, change and redistribute it, including parts of it in your own mods, as long as you credit the
original author. Fallout 4 and its DLC belong to Bethesda Softworks.

## Credits

From the original mod page. Thank you to everyone who helped shape CLM:

- **teaLz** - the Legendary Modification mod, which showed how to create craftable custom legendary modifications.
- **lilkandeekid** - help with the disintegration effects.
- **Bitflip** - permission to use the fire shield effect from his mod.
- **GLITCHEDMATRIX** - effects from the Fireclaw Whisky mod.
- **Sean_s** - explosion effects from the Grenade Expansion Pack.
- **Granverion** - suggested the Assaultron head laser effect.
- **fireundubh** - the script that adds the configuration holotape to the player's inventory without crashing.
- **shavkacagarikia** - help with the custom script behind Shavka's Explosive Striking.
- **keltas** - discovered that setting a weapon's ammo to none gives infinite ammo, the basis of the Factorium legendaries.
- **cdante** - help with scripts.
- **DankRafft** - years of compatibility patches for Legendary Crafting Framework, Crafting Framework and LEO.
- Everyone who sent requests, bug reports and feedback on Nexus Mods and Bethesda.net.

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER, ZEALOT
import random

class TuTBot(sc2.BotAI):
    async def on_step(self, iteration):
        
        await self.distribute_workers()
        await self.build_workers()
        await self.building_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def build_workers(self):
        if self.units(PROBE).amount < 70:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
    
    async def building_pylons(self):
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await self.build(PYLON, near = nexuses.first)

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            gas = self.state.vespene_geyser.closer_than(15.0, nexus)
            for i in gas:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(i.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, i).exists:
                    await self.do(worker.build(ASSIMILATOR, i))
    async def expand(self):
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            if self.units(PROBE).amount > 20*(self.units(NEXUS).amount):
                await self.expand_now()

    async def offensive_force_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random

            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if not self.units(CYBERNETICSCORE):
                    if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                        await self.build(CYBERNETICSCORE, near=pylon)
                        
            elif len(self.units(GATEWAY)) < self.units(NEXUS).amount*3:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    if self.units(GATEWAY).amount is not 1 and self.units(NEXUS).amount is 1:
                        await self.build(GATEWAY, near=pylon)
                    else:
                        self.expand()
                    

    
    async def build_offensive_force(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            unitB = random.choice([ZEALOT,STALKER])
            if self.can_afford(unitB) and self.can_feed(unitB):
                await self.do(gw.train(unitB))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        if self.units(STALKER).amount + self.units(ZEALOT).amount > 15:
            for s in self.units(STALKER).idle:
                await self.do(s.attack(self.find_target(self.state)))
            for z in self.units(ZEALOT).idle:
                await self.do(z.attack(self.find_target(self.state)))

        elif self.units(STALKER).amount + self.units(ZEALOT).amount > 3:
            if len(self.known_enemy_units) > 0:
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))
                for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(random.choice(self.known_enemy_units)))



run_game(maps.get("(2)AcidPlantLE"), [
    Bot(Race.Protoss, TuTBot()),
    Computer(Race.Terran, Difficulty.Hard)
], realtime=False)
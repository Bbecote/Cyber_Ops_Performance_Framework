"""
Agent file for the Mesa based ABM
Cyber Performance Computational Model
Submitted to Dakota State University in partial fulfillment of the requirements for the degree of PhD Cyber Operations
__author__ =  Briant Becote
__license__ Mesa framework licensing at https://docs.mesa3d.org/license.html
__email__ = "briant.becote@trojans.dsu.edu"
__status__ = "Production"
"""

import mesa
import operator
import math

#----------Global References----------#

#Self Efficacy and Skill Assumption 85% skill, 15% self-efficacy
skills_modifier = .65
self_efficacy_modifier = .15
network_strength_modifier = .02

#----------Operator Agents------------#
class Operator(mesa.Agent):
    def __init__(self, unique_id, model, pos, mission, efficacy, skills, phase):
        super().__init__(unique_id, model) 
        self.security_strength  = self.model.security_strength
        self.pos = pos
        self.mission = mission
        self.efficacy = efficacy
        self.skills = skills
        self.phase = phase    
        #---Attack Agent Parameters
        self.identified_nodes = []
        self.exploit_list = []
        self.exploited_nodes = []
        self.caught = 0
        #---Defense Agent Parameters
        self.monitor_list = []
        self.repair_list = []
        self.recovery_list = []
        self.exhausted = 0

        attacker_network_modifier = network_strength_modifier * network_strength_modifier
        defender_network_modifier = abs(network_strength_modifier -100) * network_strength_modifier

        self.defender_ability_modifier = skills * skills_modifier + efficacy * self_efficacy_modifier + defender_network_modifier
        self.attacker_ability_modifier = skills * skills_modifier + efficacy * self_efficacy_modifier + attacker_network_modifier

    #---Print Utility Method
    def __str__(self):
        return self.unique_id
        
    #---Step Method - Entry point for each step of the model
    def step(self):
        if self.mission == "ATTACKER":
            self.attack_network()
        elif self.mission == "DEFENDER":
            self.defend_network()
            
#----------Attack Functions------------#       
     
        #Forces Attacker Agent to wait if Attacker was caught
    def attack_network(self):
        if self.caught > 0:
            self.caught -= 1
            return
        #Directs Attacker Agent based on phase of attack
        if self.identified_nodes:
            self.update_identified_nodes()
        else: self.phase = "search"
        if self.phase == "attack":
            self.attack()
        elif self.phase == "c2":
            self.c2()
        else:
            self.search()  

    #---Update Attacker's identified node list
    def update_identified_nodes(self):
        self.identified_nodes = list(set(self.identified_nodes))
        attack_list = self.identified_nodes.copy()
        for node in attack_list:
            if node.exposure == "zero day secure" or node.exposure == "offline":
                self.identified_nodes.remove(node)
        if not self.identified_nodes:
            self.phase = "search"

    #---Helper function once a target node is found
    def find_node(self, target_node):
        target_node.exposure = "exposed"
        target_node.status = self.random.randint(5, 7)
        self.model.grid.move_agent(self, target_node.pos)
        self.identified_nodes.append(target_node)
        self.phase = "attack"
        self.efficacy += .01
    
    #---Helper function, attacks the target node
    def attack_node(self, target_node, attack_modifier):
        target_node.status = self.clamp(target_node.status - self.attacker_ability_modifier/attack_modifier, -1, 11)
        target_node.update_node_exposure()

    #---1st Phase of Attacker Agent, searching for nodes on the network to attack
    def search(self):
        node_list = [agent for agent in self.model.schedule.agents if type(agent) is Node]
        node_count = len(node_list)
        #Search range is probability based on number of nodes (attack surface) and search skill + efficacy
        search_probability = ( 1 + node_count / 30) * self.attacker_ability_modifier * .015
        if search_probability > self.random.uniform(0, 1):
            target_node = self.random.choice(node_list)
            self.find_node(target_node)
            return
        #If self efficacy is high enough vs random factor, ask another attacker for a node to attack.
        else:
            if self.efficacy > self.random.uniform(0, 1):
                available_attackers = list([agent for agent in self.model.schedule.agents if type(agent) is Operator and agent.mission == "ATTACKER" and agent is not self])
                if available_attackers:
                    another_attacker = self.random.choice(available_attackers)
                    if another_attacker.identified_nodes:
                        target_node = self.random.choice(another_attacker.identified_nodes)
                        self.find_node(target_node)
                        return
            #Attacker unable to find a node
            self.efficacy -= .01
            #Updates view to simulate searching the network
            self.model.grid.move_agent(self, (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height)))

    #---2nd Phase of Attack Agent, attacking identified nodes by reducing status from exposed to infiltrated to exploited
    def attack(self):
        #Conduct attack on up to 3 exposed nodes, lowering the node status
        attack_list = self.identified_nodes.copy()
        attack_attempts = math.floor(self.attacker_ability_modifier)
        for index in range(attack_attempts):
            key = operator.attrgetter("status")
            attack_list.sort(key = key)
            target_node = attack_list[0]
            self.attack_node(target_node, 7)
            #Minor setback from defender update, but will continue trying
            if target_node.exposure == "secure":
                self.efficacy -= .01
            #Attacker succeeds, and moves on to C2 phase
            elif target_node.exposure == "exploited":
                self.phase = "c2"
                self.efficacy += .05

    
    #---3rd Phase of Attack Agent, C2, Attempting a lateral move across the network
    def c2(self):
        node_list = [agent for agent in self.model.schedule.agents if type(agent) is Node]
        node_count = len(node_list)
        attack_list = list([node for node in self.identified_nodes if node.exposure != "exploited"])
        unidentified_list = [node for node in node_list if node not in attack_list]
        if unidentified_list:
            #Improved probability of search function based on exploitated node lateral move
            search_probability = ( 2.5 + node_count / 30) * self.attacker_ability_modifier * .015
            if search_probability > self.random.uniform(0, 1):
                target_node = self.random.choice(unidentified_list)
                self.find_node(target_node)
                self.phase = "c2"
                attack_list.append(target_node)
        if attack_list:
            for node in attack_list:
                self.attack_node(node, 3)
        

#----------Defend Functions------------#
    def defend_network(self):
         #Forces Defender Agent to wait if Defender recovered a node
        if self.exhausted > 0:
            self.exhausted -= 1
            return
        #Directs Defender Agent based on phase of attack
        if self.phase == "monitor":
            self.monitor()
        elif self.phase == "repair":
            self.repair()
        else:
            self.recovery()

    def monitor_node(self, node):
        node.monitored = True
        self.monitor_list.append(node)

    #---1st Phase of Defender Agent, monitoring and patching nodes on the network
    def monitor(self):
        defenders = [agent for agent in self.model.schedule.agents if type(agent) is Operator and agent.mission == "DEFENDER"]
        defender_count = len(defenders)
        node_list = [agent for agent in self.model.schedule.agents if type(agent) is Node]
        node_count = len(node_list)
        #Assigning nodes to defenders
        nodes_remaining = list([node for node in node_list if node.monitored is False])
        if self.monitor_list and nodes_remaining:
            self.monitor_node(nodes_remaining.pop())
        if not self.monitor_list:
            nodes_assign_count = min((math.floor(node_count/defender_count), len(nodes_remaining)))
            for index in range(nodes_assign_count):
                self.monitor_node(nodes_remaining.pop())
        if not self.monitor_list:
            if nodes_remaining:
                self.monitor_node(nodes_remaining.pop())
            else:
                self.monitor_list.append(self.random.choice(node_list))
        #Monitor/Patch nodes
        for index in range(math.floor(self.defender_ability_modifier)):
            key = operator.attrgetter("status")
            self.monitor_list.sort(key = key)
            node = self.monitor_list[0]
            node.status = self.clamp(node.status + self.defender_ability_modifier / 7, -1, 11)
            node.update_node_exposure()
            if node.exposure != "secure" and node.exposure != "zero day secure":
                self.repair_list.append(node)
                self.phase = "repair"
                #If self efficacy is high enough vs random factor, ask another defender to assist in repair
                if self.efficacy > self.random.uniform(1, 10):
                    available_defenders = list([defender for defender in defenders if defender.phase == "monitor" and defender is not self])
                    if available_defenders:
                        friend = self.random.choice(available_defenders)
                        friend.repair_list.append(node)
                        friend.phase = "repair"

    #---2nd Phase of Defender Agent, repairing nodes. These nodes are identified as needing direct attention
    def repair(self):
        defenders = [agent for agent in self.model.schedule.agents if type(agent) is Operator and agent.mission == "DEFENDER"]
        if not self.repair_list:
            self.phase = "monitor"
            return
        node = self.random.choice(self.repair_list)
        node.status = self.clamp(node.status + self.defender_ability_modifier / 3, -1, 11)
        node.update_node_exposure()
        #Repair complete
        if node.exposure == "secure" or node.exposure == "zero day secure":
            self.efficacy += .05
            self.model.grid.move_agent(node, (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height)))
            self.repair_list.remove(node)
        #Cyber attack discovered, moving into cyber recovery response
        elif node.exposure == "exploited" or node.exposure == "infiltrated":
            self.phase = "recovery"
            self.recovery_list.append(node)
            self.repair_list.remove(node)
            self.efficacy -= .05
            available_defenders = list([defender for defender in defenders if defender.phase == "monitor" and defender is not self])
            #If self efficacy is high enough vs random factor, ask all available defenders to assist in recovery
            if self.efficacy > self.random.uniform(0, 1):
                if available_defenders:
                    friend = self.random.choice(available_defenders)
                    friend.recovery_list.append(node)
                    friend.phase = "recovery"
        elif node.exposure == "offline":
            self.repair_list.remove(node)

    #---3rd Phase of Defender Agent, recover nodes. These nodes are identified as exploited, and need to be brought offline to prevent further attack
    def recovery(self):
        if not self.recovery_list:
            self.phase = "monitor"
            self.monitor()
            return
        node = self.random.choice(self.recovery_list)
        if node.status > 7:
            self.recovery_list.remove(node)
            if self.recovery_list:
                self.recovery()
            else:
                self.phase = "monitor"
                return
        else:
            node.status = self.clamp(node.status + self.defender_ability_modifier / 3, -1, 11)
            node.update_node_exposure()  
            if node.status > 7:
                self.model.grid.move_agent(node, (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height)))
                #Node and Defender are offline during repair, 4 to 10 steps
                node.exposure = "offline"
                node.offline_counter += self.random.randint(4,10)
                self.exhausted += node.offline_counter
                self.recovery_list.remove(node)
                self.efficacy += .1
                if not self.recovery_list:
                    self.phase = "monitor"
                #Check if there is an attacker on this square, if so, that attacker is "caught"
                grid_contents = self.model.grid.get_cell_list_contents([node.pos])
                attackers_present = list(filter(lambda x: type(x) == Operator and x.mission == "ATTACKER", grid_contents))
                for attacker in attackers_present:
                    if node in attacker.identified_nodes:
                        attacker.identified_nodes.remove(node)
                    attacker.caught += self.random.randint(10,20)

#----------Helper Functions------------#

    #---Limits min and max node status to -1 and 11
    def clamp(self, n, smallest, largest):
        return max(smallest, min(n, largest))

#----------Node Agent------------#
class Node(mesa.Agent):
    def __init__(self, unique_id, model, pos, status):
        super().__init__(unique_id, model)
        #self.type = "Node"
        self.pos = pos
        self.status = status
        self.exposure = "secure"
        self.monitored = False
        self.offline_counter = 0

    #---Aligns node numerical status with description
    def update_node_exposure(self):
        if self.status >9 and self.exposure != "offline":
            self.exposure = "zero day secure"
        elif self.status >= 7 and self.exposure != "offline":
            self.exposure = "secure"
        elif self.status >= 4 and self.exposure != "offline":
            self.exposure = "exposed"
        elif self.status >= 2.5 and self.exposure != "offline":
            self.exposure = "infiltrated"
        elif self.exposure != "offline":
            self.exposure = "exploited"
        
    #---Print Utility Method
    def __str__(self):
        return self.unique_id  


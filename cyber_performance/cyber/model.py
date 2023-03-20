"""
Model file for the Mesa based ABM
Cyber Performance Computational Model
Submitted to Dakota State University in partial fulfillment of the requirements for the degree of PhD Cyber Operations
__author__ =  Briant Becote
__license__ Mesa framework licensing at https://docs.mesa3d.org/license.html
__email__ = "briant.becote@trojans.dsu.edu"
__status__ = "Production"
"""

from typing import Type, Callable
import pandas as pd
import mesa
from cyber.agents import Node, Operator
import matplotlib.pyplot as plt

#----------Data Collector Functions------------#
class RandomActivationByTypeFiltered(mesa.time.RandomActivationByType):
    #Adopted from wolf & sheep example
    #Overwrites the mesa model class function to enable return of agent count by type
    def get_type_count(
        self, 
        type_class: Type[mesa.Agent],
        filter_func: Callable[[mesa.Agent], bool] = None,
    ) -> int:
        count = 0
        for agent in self.agents_by_type[type_class].values():
            if filter_func is None or filter_func(agent):
                count += 1
        return count
    
def get_availability_index(self):
    print(self.availability_index)
    total_node_count = self.node_count * self.step_count
    return (total_node_count - self.exploited_count - self.offline_count)  / total_node_count

def get_sustainability_index(self):
    return self.step_count

def get_offline_exploited_count(self):
    return self.offline_count + self.exploited_count


class Cyber(mesa.Model):

    def __init__(self,
        #----------Model
        width = 35,
        height = 35,
        node_count = 15,
        security_strength = 70,
        attack_or_defend = "defend",
        phase = "",
        offline_count = 0,
        cyberattack_costs = 1,
        defender_costs = 1,
        
        #----------Friendly
        friendly_count = 2,
        friendly_skills = 7,
        friendly_efficacy = 7,

        #----------Adversary
        adversary_count = 4,
        adversary_skills = 7,
        ):

        #----------Model
        super().__init__()
        self.width = width
        self.height = height
        self.node_count = node_count
        self.node_model_count = 0 
        self.security_strength = security_strength
        self.attack_or_defend = attack_or_defend
        self.cyberattack_costs = cyberattack_costs
        self.defender_costs = defender_costs
        self.step_count = 0

        #----------Agent Utility
        self.offline_count = offline_count
        self.availability_index = 1
        self.sustainability_index = 1 
        self.exploited_count = 0
        self.phase = phase

        #----------Friendly
        self.friendly_count = friendly_count
        self.friendly_efficacy = friendly_efficacy
        self.friendly_skills = friendly_skills

        #----------Adversary
        self.adversary_count = adversary_count 
        self.adversary_skills = adversary_skills

        self.schedule = RandomActivationByTypeFiltered(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        self.running = True
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Availability Index": get_availability_index,
                "Sustainability Index": get_sustainability_index,
                "Zero Day Secure": lambda a: a.schedule.get_type_count(Node, lambda x: x.exposure == "zero day secure"),
                "Secured Nodes": lambda a: a.schedule.get_type_count(Node, lambda x: x.exposure == "secure"),
                "Exposed Nodes": lambda a: a.schedule.get_type_count(Node, lambda x: x.exposure == "exposed"),
                "Inflitrated Nodes": lambda a: a.schedule.get_type_count(Node, lambda x: x.exposure == "infiltrated"),
                "Exploited Nodes": lambda a: a.schedule.get_type_count(Node, lambda x: x.exposure == "exploited"),
                "Offline": lambda a: a.schedule.get_type_count(Node, lambda x: x.exposure == "offline"),
                }
            )

    # Create Friendly Defenders:
        if self.attack_or_defend == "defend":
            for i in range(self.friendly_count):
                efficacy = self.friendly_efficacy
                skills = self.friendly_skills
                x = 0 
                y = i
                if y > 34:
                   x = i - 34
                   y = 0
                if x > 34:
                   x -= 34
                   y = 34
                mission = "DEFENDER"
                phase = "monitor"
                defender = Operator("defender_" + str(i), self, (x, y), mission, efficacy, skills, phase)
                self.grid.place_agent(defender, (x, y))
                self.schedule.add(defender)
    #Create Adversary Attackers
            for i in range(self.adversary_count):
                efficacy = 5
                skills = self.adversary_skills
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                mission = "ATTACKER"        
                phase = "search"
                attacker = Operator("attacker_" + str(i), self, (x, y), mission, efficacy, skills, phase)
                self.grid.place_agent(attacker, (x, y))
                self.schedule.add(attacker)
    # Create Adversary Defenders
        else:
            for i in range(self.adversary_count):    
                efficacy = 5
                skills = self.adversary_skills
                x = 0 
                y = i
                if y > 34:
                   x = i - 34
                   y = 0
                if x > 34:
                   x -= 34
                   y = 34
                mission = "DEFENDER"
                phase = "monitor"
                defender = Operator("defender_" + str(i), self, (x, y), mission, efficacy, skills, phase)
                self.grid.place_agent(defender, (x, y))
                self.schedule.add(defender)
    #Create Friendly Attackers
            for i in range(self.friendly_count):    
                efficacy = self.friendly_efficacy
                skills = self.friendly_skills
                x = self.random.randrange(self.width)
                y = self.random.randrange(self.height)
                mission = "ATTACKER"        
                phase = "search"
                attacker = Operator("attacker_" + str(i), self, (x, y), mission, efficacy, skills, phase)
                self.grid.place_agent(attacker, (x, y))
                self.schedule.add(attacker)

    # Create Nodes:
        for i in range(self.node_count):
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            status = self.security_strength + self.random.randint(-1, 1)
            node = Node("node_" + str(i), self, (x, y), status/10)
            self.grid.place_agent(node, (x, y))
            self.schedule.add(node)

    # Each step of the simulation begins here
    def step(self):
        self.step_count += 1
        self.sustainability_index = self.step_count
        self.availability_index = get_availability_index(self)
        self.schedule.step()
        self.datacollector.collect(self)
        node_list = [agent for agent in self.schedule.agents if type(agent) is Node]
        agent_list = [agent for agent in self.schedule.agents if type(agent) is Operator]
        print("<--------------END STEP", self.step_count, "-------------->", )
        for node in node_list:
            if node.offline_counter > 1:
                node.offline_counter -= 1
                self.offline_count += 1
            elif node.offline_counter == 1:
                node.offline_counter = 0
                self.offline_count += 1
                node.exposure = ""
                node.update_node_exposure()
            print("All nodes and status:", node.unique_id, node.status, node.exposure, node.offline_counter)
        for agent in agent_list:
            if agent.mission == "ATTACKER":
                print("Attacker ID and status:", agent.unique_id, agent.phase, agent.caught, "Identified List:", *agent.identified_nodes)
            if agent.mission == "DEFENDER":
                print("Defender ID and status:", agent.unique_id, agent.phase, agent.exhausted, "Monitor List:", *agent.monitor_list)
        exploited_list = [node for node in node_list if node.exposure == "exploited"]
        self.exploited_count += len(exploited_list)
        print("Exploited Count:", self.exploited_count)
        print("Outage Count:", self.exploited_count + self.offline_count)
        if len([agent for agent in self.schedule.agents if type(agent) is Node]) == len([agent for agent in self.schedule.agents if type(agent) is Node and agent.exposure == "offline" or type(agent) is Node and agent.exposure == "exploited"]):
            #print("Simulation Halted - Attackers completely crippled the network")
            batch = self.datacollector.get_model_vars_dataframe()
            batch.to_csv("Model Testing.csv")
            self.running = False
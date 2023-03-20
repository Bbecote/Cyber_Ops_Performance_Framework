"""
Server file for the Mesa based ABM
Cyber Performance Computational Model
Submitted to Dakota State University in partial fulfillment of the requirements for the degree of PhD Cyber Operations
__author__ =  Briant Becote
__license__ Mesa framework licensing at https://docs.mesa3d.org/license.html
__email__ = "briant.becote@trojans.dsu.edu"
__status__ = "Production"
"""

import mesa
from .agents import Operator, Node
from cyber.model import Cyber



#----------Visual Characteristics------------#
def cyber_portrayal(agent):
    if agent is None:
        return
    
    portrayal = {}

#----------Display Attackers------------#
    if type(agent) is Operator:
        if agent.mission == "ATTACKER":
            portrayal["Shape"] = "cyber/resources/hacker.png"
            portrayal["scale"] = 0.9
            portrayal["Layer"] = 1

#----------Don't Display Defenders------------#
        if agent.mission == "DEFENDER":
            portrayal["Shape"] = "cyber/resources/defender.png"
            portrayal["scale"] = 1.3
            portrayal["Layer"] = 1

#----------Display Nodes------------#
    elif type(agent) is Node and agent.offline_counter == 0 and agent.exposure != "exploited":
        portrayal["Shape"] = "cyber/resources/network.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 2
        portrayal["text"] = 1
        portrayal["text_color"] = "White"       
    else:
        portrayal["Shape"] = "cyber/resources/hacked1.png"
        portrayal["scale"] = 1.3
        portrayal["Layer"] = 2
        portrayal["text"] = 1
        portrayal["text_color"] = "White"   
    return portrayal

#----------Custom Display Methods------------#
#These methods are used to print to the dashboard during simulation
def get_offline_count(model):
    return model.offline_count + model.exploited_count

def get_defender_cost(model):
    if model.attack_or_defend == "defend":
        cost = round(model.friendly_count * model.defender_costs / 365 * model.step_count, 2)
        return cost
    else:
        cost = round(model.adversary_count * model.defender_costs / 365 * model.step_count, 2)
        return cost

def get_offline_cost(model):
    return model.cyberattack_costs * get_offline_count(model)

def get_total_cost(model):
    return get_offline_cost(model) + round(get_defender_cost(model), 2)

def network_compromised(model):
    node_count = len([agent for agent in model.schedule.agents if type(agent) is Node])
    compromised_count =  len([agent for agent in model.schedule.agents if type(agent) is Node and agent.exposure == "offline" or type(agent) is Node and agent.exposure == "exploited"])
    if compromised_count == 0:
        return f"Percentage of Network Compromised: %0"
    else:
        return f"Percentage of Network Compromised: {round(compromised_count / node_count * 100)}%"
    
def get_availability_index(model):
    return f"Availability Index: {round(model.availability_index, 4)}"

def get_sustainability_index(model):
    return f"Sustainability Index: {model.sustainability_index}/1000"

def get_text_data(model):
    return f"Total Exploitation Outages: {get_offline_count(model)}, Cost for Outages: ${get_offline_cost(model)}, Cost of Defenders (days culmulative): ${get_defender_cost(model)}, Total Cost: ${get_total_cost(model)}"
#----------User Definable Parameters------------#
#Must match up to model.py parameters
model_params = {
    #"simulations_count": mesa.visualization.Slider("Number of Simulations to run", 1, 1, 100, description = "Run multiple simulations and receive the average of the results"),
    "node_count": mesa.visualization.Slider("Number of Network Access Nodes", 15, 1, 100, description = "Change this to alter the number of access nodes"),
    "security_strength": mesa.visualization.Slider("Network Initial Security Strength", 50, 1, 100, description = "Establishes approximate node security"),
    "attack_or_defend": mesa.visualization.Choice("Friendly Forces Mission", "defend", ["defend", "attack"], description = "Determines how user input of self-efficacy is applied"),
    "cyberattack_costs": mesa.visualization.Slider("Dollar Cost of an Outtage per Day", 20000, 1000, 200000, 100000, description = "Average cost per network element of a cyber attack"),
    "defender_costs": mesa.visualization.Slider("Dollar Cost of a Defender per Year", 70000, 30000, 250000, 10000, description = "Average cost per Cyber Defender"),
    
    #---Friendly Variables
    "friendly_count": mesa.visualization.Slider("Number of Cyber Friendly Operators", 5, 1, 100, description = "Change this to alter the number of friendly operators"),
    "friendly_skills": mesa.visualization.Slider("Friendly Forces Skills", 7, 1, 10, .1, description = "Establishes a baseline for cyber skills and abilities"), 
    "friendly_efficacy": mesa.visualization.Slider("Friendly Forces Team-Efficacy", 7, 1, 10, description = "A dynamic influencial characteristic from the COSES survey"),
    
    #---Adversary Variables
    "adversary_count": mesa.visualization.Slider("Number of Adversary Operators", 5, 1, 100, description = "Change this to alter the number of adversaries"),
    "adversary_skills": mesa.visualization.Slider("Adversary Skills", 7, 1, 10, .1, description = "Establishes a baseline for cyber skills and abilities"),
    }

#----------Create Grid Visualization------------#
canvas_element = mesa.visualization.CanvasGrid(cyber_portrayal, 35, 35, 750, 750)

#----------Create Line Chart Visualization------------#
line_chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Offline", "Color": "#000000"},
        {"Label": "Zero Day Secure", "Color": "#00AA00"},
        {"Label": "Secured Nodes", "Color": "#0000FF"},
        {"Label": "Exposed Nodes", "Color": "#AA0000"},
        {"Label": "Infiltrated Nodes", "Color": "#FFA500"},
        {"Label": "Exploited Nodes", "Color": "#FF0000"},
    ], data_collector_name = 'datacollector'
)

#----------Launches Visualization------------#
network = mesa.visualization.NetworkModule(cyber_portrayal, 100, 100)
server = mesa.visualization.ModularServer(Cyber, [canvas_element, line_chart_element, get_sustainability_index, get_availability_index, network_compromised, get_text_data], "Cyber Performance Model", model_params)
server.port = 8521
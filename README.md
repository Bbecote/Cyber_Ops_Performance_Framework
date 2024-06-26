# Cyber Operations Performance Framework
An Agent-Based Computational Model built on the [Mesa](https://github.com/projectmesa/mesa) Python 3+ framework used to analyze and predict Cyber Operations and provides ROI on cyber resource allocation.

This computational model was developed and submitted to Dakota State University in partial fulfillment of the requirements for the degree of [Ph.D. Cyber Operations](https://dsu.edu/programs/phdco/index.html).  The dissertation can be downloaded and reviewed [here](https://scholar.dsu.edu/theses/406/).

The Cyber Operations Performance Computational Model is designed to be used alongside the [Cyber Operations Self-Efficacy Scales (COSES)](https://form.jotform.com/230343475113447) (publication pending).  The COSES provides the model-users with a behavioral input of operator efficacy used to align simulation results with real-world operator behavioral input.  While this input can be simulated or estimated, the use of the scales is highly recommended.

The Cyber Operations Performance Computational Model:

![Cyber Ops ABM image](https://github.com/Bbecote/Cyber_Ops_Performance_Framework/blob/main/images/Model_Start.png "Cyber Ops Model at start up, default parameters")

 _Above: Cyber Ops Model at start up, default parameters_


![Cyber Ops ABM image](https://github.com/Bbecote/Cyber_Ops_Performance_Framework/blob/main/images/Model_Step20.png "Cyber Ops Model at step 20, default parameters")

_Above: Cyber Ops Model at step 20, default parameters_

# Features
* Easy-to-use assessment tool for real-world cyber operations.
* Great flexibility for user input across a wide range of user parameters. 
* User-based ROI feedback for cyber logistical resources.
* Visual and text dashboard for real-time analysis.
* Research complex systems through cyber operations to view emergence, tipping points, nonlinear phenomena, and diminishing returns. 

# Using the Cyber Operations Performance Agent-Based Model
* Users who want to install and run the model locally can pull the cyber_performance python script and reference [Mesa's Documentation](https://mesa.readthedocs.io/en/stable/) for framework installation.

Once Mesa is installed, run the computational model from the command line within the cyber_performance folder.  To run a single simulation with dashboard visualization:

`python3 run.py`

To run batch simulations (no dashboard):

`python3 batch.py`

Edit the batch.py file to update the simulation parameters desired for batch simulations.

* The model will also be hosted online for limited use at (Link Pending).

# Limitations
Metrics are only as good as the validity and reliability of their measurement. The design goal of this computational model is the flexibility to adjust the agent-based modeling parameters or underlying fundamentals as required. Without direct empirical data to compare, the computational model’s ability to accurately predict performance under various conditions deserves continued testing. When leveraged by organizations that have direct access to the sensitive data that defines cyber operations, comparison between the model's results and real-world findings will allow for model adjustment as necessary.  With sufficient input, cyber analysis and prediction can be achieved with a much higher degree of confidence for an organization's specific use-cases.

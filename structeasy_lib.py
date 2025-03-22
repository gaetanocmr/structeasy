"""
Gaetano Camarda V.1.0 - 03/2025
https://www.linkedin.com/in/ing-gaetano-camarda

"""

from structeasy.structeasy_class import *
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

def import_geofile(filename):
    """This function imports a .geo file and returns a dictionary with nodes and elements.
    respecting the defined classes in structeasy.
    
    Recognized entities are:
    - Nodes
    - Lines

    Input:
    filename: str, path to the .geo file

    Output:
    - nodes_db: dict, dictionary with nodes
    - elements_db: dict, dictionary with elements

    Gaetano Camarda - 03/2025 V.1.0 
    """

    from gmsh import initialize, open, model, finalize # Import gmsh functions
    def assign_tag(nnumber, eltype, model_tags):
        """This function assigns a tag to a node or element based on the physical group it belongs to."""
        tag = -1
        for tag_ in model_tags:
            eltype_ = tag_[0] 
            if eltype_ == eltype and nnumber in model.getEntitiesForPhysicalGroup(eltype, tag_[1]).tolist():
                tag = tag_[1]
        return tag

    """.geo file importer"""
    initialize() # Initialize gmsh
    open(filename) # Open the file
    nodes = model.getEntities(0) # Get the nodes of the model
    lines = model.getEntities(1) # Get the lines of the model   
    model_tags = model.getPhysicalGroups() # Get the physical groups of the model
    nodes_db = {} # Initialize the nodes dictionary
    for i in nodes:
        nnumber = i[1]
        x, y, z = model.getValue(0, nnumber, ()).tolist()
        tag = assign_tag(nnumber, 0, model_tags)
        nodes_db[nnumber] = Node(nnumber, x, y, z, tag)

    elements_db = {} # Initialize the elements dictionary
    for e in lines:
        enumber = e[1]
        bound_node = model.getBoundary([e]) # Get the nodes of the element
        nodes = ([nodes_db[n[1]] for n in bound_node])
        tag = assign_tag(enumber, 1, model_tags)
        elements_db[enumber] = Element(enumber, nodes, tag, etype = 'uniaxial')

    finalize()
    return nodes_db, elements_db
    

def plot_model(nodes_db, elements_db, show_numbers=False, show_tags=False, color_by_tag=False, save_html=False, filename='plot.html', show_legend=False):
    """"
    Plots a 3D model based on the nodes and elements dictionaries using Plotly.
    nodes_db (dict): Dictionary containing node objects with attributes x, y, z, and tag.
    elements_db (dict): Dictionary containing element objects with attributes nodes (list of node objects) and tag.
    show_numbers (bool, optional): If True, show element and node numbers. Defaults to False.
    show_tags (bool, optional): If True, show tags associated with elements and nodes. Defaults to False.
    color_by_tag (bool, optional): If True, color elements and nodes based on their tags. Defaults to False.
    save_html (bool, optional): If True, save the plot to an HTML file. Defaults to False.
    filename (str, optional): Name of the HTML file to save the plot. Defaults to 'plot.html'.
    show_legend (bool, optional): If True, show the legend in the plot. Defaults to False.
    Returns:
    None
    This function creates a 3D scatter plot for nodes and a 3D line plot for elements using Plotly.
    It allows customization of the plot by showing numbers, tags, coloring by tags, and saving the plot as an HTML file.
    
    Gaetano Camarda - 03/2025 V.1.0
    """
    import plotly.graph_objects as go
    import matplotlib.cm as cm

    # Define colors
    if color_by_tag:
        tags = list(set([n.tag for n in nodes_db.values() if n.tag != -1] + [e.tag for e in elements_db.values() if e.tag != -1]))
        colors = cm.rainbow(np.linspace(0, 1, len(tags)))
        tag_color_map = {tag: f'rgb({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)})' for tag, color in zip(tags, colors)}
    else:
        tag_color_map = {}

    # Create a 3D scatter plot for nodes
    node_x = [node.x for node in nodes_db.values()]
    node_y = [node.y for node in nodes_db.values()]
    node_z = [node.z for node in nodes_db.values()]
    node_color = [tag_color_map.get(node.tag, 'red') for node in nodes_db.values()] if color_by_tag else ['red'] * len(nodes_db)

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text' if show_numbers or show_tags else 'markers',
        marker=dict(size=8, color=node_color),  # Use node_color for nodes
        text=[f'{nnumber}<br>Tag: {node.tag}' if show_tags else str(nnumber) for nnumber, node in nodes_db.items()] if show_numbers else None,
        textposition='middle right',
        textfont=dict(color=node_color),
        showlegend=show_legend
    )

    # Create a 3D line plot for elements
    element_traces = []
    for enumber, element in elements_db.items():
        x = [node.x for node in element.nodes]
        y = [node.y for node in element.nodes]
        z = [node.z for node in element.nodes]
        color = tag_color_map.get(element.tag, 'black') if color_by_tag else 'black'
        text = f'{enumber}<br>Tag: {element.tag}' if show_tags else str(enumber) if show_numbers else None

        # Calculate the midpoint for text position
        mid_x = sum(x) / len(x)
        mid_y = sum(y) / len(y)
        mid_z = sum(z) / len(z)

        element_trace = go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            line=dict(color=color, width=4),  # Use color for elements
            showlegend=show_legend
        )

        # Add text at the midpoint
        if show_numbers or show_tags:
            mid_trace = go.Scatter3d(
                x=[mid_x], y=[mid_y], z=[mid_z],
                mode='text',
                text=[text],
                textposition='top center',
                textfont=dict(color=color),
                showlegend=False
            )
            element_traces.append(mid_trace)

        element_traces.append(element_trace)

    # Create the figure
    fig = go.Figure(data=[node_trace] + element_traces)

    # Set axis labels and layout
    fig.update_layout(
        scene=dict(
            xaxis_title='X axis',
            yaxis_title='Y axis',
            zaxis_title='Z axis',
            xaxis=dict(backgroundcolor="#f0f0f0", tickfont=dict(color='darkgrey', size=12, family='Arial')),
            yaxis=dict(backgroundcolor="#f0f0f0", tickfont=dict(color='darkgrey', size=12, family='Arial')),
            zaxis=dict(backgroundcolor="#f0f0f0", tickfont=dict(color='darkgrey', size=12, family='Arial'))
        ),
        width=800,  # Set the width of the figure
        height=600,  # Set the height of the figure
        margin=dict(l=0, r=0, b=0, t=0)  # Use tight layout
    )

    # Show the plot
    fig.show()

    # Save the plot to an HTML file if required
    if save_html:
        fig.write_html(filename)

## OPENSEES SPECIFIC FUNCTIONS
def start_model(typology):
    """
    This function let you to easily initialize the OpenseesPy model by calling:
    start_model('2d') # for 2d problems
    start_model('3d') # for 3d problems
    """
    from openseespy.opensees import wipe, model
    """Initialize opensees Model
    type = '2d'
    type = '3d'
    """
    if typology == '3d':
        wipe()
        model('basic', '-ndm', 3 ,'-ndf', 6) # Define space (3D) and DOF (6 degrees)
        print('3d model initialized')
    elif typology == '2d':
        wipe()
        model('basic', '-ndm', 2 ,'-ndf', 3) # Define space (3D) and DOF (6 degrees)
        print('2d model initialized')
    else:
        print()
        raise NameError('-- Not valid model type, try "2d" or "3d" --')

def create_nodes(nodes):
    """
    Given a node dictionary from import_gmsh function, this function will generate nodes inside the openseespy model
    """
    from openseespy.opensees import node
    for n in nodes:
        node(n, *nodes[n].coord)
    print('Structure nodes genereted on OpenSeespy')

def material_tester(matTag, strain, title='Stress-Strain Behavior', scaleStress=1):
    """
    This is a simple function to test material in OpenSeesPy:
    matTag: material tag implemented
    strain: list of strains
    title: string title of the plot
    scaleStress: if you need to convert output stresses in a specific unit

    N.B. The function will automatically plot the stress-strain graph

                                        Gaetano Camarda 2022
                                        University of Palermo
                                        v.1.0
    """
    import numpy as np
    try:
        from openseespy.opensees import testUniaxialMaterial, getStress, setStrain
        from matplotlib.pyplot import grid, plot, subplots
        testUniaxialMaterial(matTag)
        stress = []
        for eps in strain:
            setStrain(eps)
            stress.append(getStress())
        fig, ax = subplots(dpi=120)
        ax.set_title(title + ' | Material Tag: ' + str(matTag))
        ax.plot(strain, np.array(stress) / scaleStress, color='#45818e')
        ax.grid(linestyle='--', color='#e2e2e2')
        ax.set_xlabel('Strain')
        ax.set_ylabel('Stress')
    except:
        print('Please check material and openseespy definition or matplotlib library')


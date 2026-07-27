// Node color mapping
const nodeColors = {
    'Person': '#3498DB',
    'Role': '#2ECC71',
    'Project': '#E74C3C',
    'Domain': '#F39C12',
    'Tool': '#9B59B6',
    'Feature': '#1ABC9C',
    'Phase': '#E67E22',
    'Milestone': '#2C3E50',
    'Outcome': '#27AE60',
    'Deliverable': '#2980B9',
    'Dataset': '#8E44AD'
};

function createGraph(nodes, edges) {
    const elements = [
        ...nodes.map(n => ({
            data: {
                id: n.id,
                label: n.name,
                type: n.type,
                ...n.properties
            },
            style: {
                'background-color': nodeColors[n.type] || '#95A5A6'
            }
        })),
        ...edges.map(e => ({
            data: {
                id: e.source + '-' + e.target,
                source: e.source,
                target: e.target,
                label: e.relation
            }
        }))
    ];
    
    return {
        container: document.getElementById('cy'),
        elements: elements,
        style: [
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'color': '#fff',
                    'font-size': '12px',
                    'font-weight': 'bold',
                    'width': '60px',
                    'height': '60px',
                    'border-width': 2,
                    'border-color': '#2C3E50'
                }
            },
            {
                selector: 'edge',
                style: {
                    'label': 'data(label)',
                    'font-size': '10px',
                    'text-rotation': 'autorotate',
                    'width': 2,
                    'line-color': '#7F8C8D',
                    'target-arrow-color': '#7F8C8D',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }
        ],
        layout: {
            name: 'cose',
            idealEdgeLength: 100,
            nodeRepulsion: 400000,
            edgeElasticity: 100,
            nestingFactor: 5,
            gravity: 80,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
        }
    };
}

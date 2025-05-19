# import packages
import pandas as pd
import ast
from collections import defaultdict, deque
import networkx as nx
import os



#define fucntions
def preprocess_flows(df_flows, commodity):
    """Parse Edge strings and filter by commodity."""
    df_flows = df_flows[df_flows['Commodity'] == commodity].copy()
    df_flows['Edge'] = df_flows['Edge'].apply(ast.literal_eval)
    return df_flows

def build_flow_and_cost_dicts(df_flows, df_edges, commodity):
    """Build dictionaries for flows and edge costs."""
    flow_dict = defaultdict(float)
    for _, row in df_flows.iterrows():
        flow_dict[row['Edge']] += row['Flow']

    cost_dict = {}
    for _, row in df_edges[df_edges['Commodity'] == commodity].iterrows():
        cost_dict[(row['Source'], row['Destination'])] = row['costs_edge']

    return flow_dict, cost_dict

def get_longest_chain_before_nodes(df_flows, commodity):
    """Compute the longest chain (depth) and path for each node."""
    df = df_flows[df_flows['Commodity'] == commodity].copy()

    G = nx.DiGraph()
    for _, row in df.iterrows():
        src, dst = row['Edge']
        G.add_edge(src, dst)

    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Graph must be a DAG for longest path calculation.")

    longest_chains = {}
    memo = {}

    def longest_path_to(node):
        if node in memo:
            return memo[node]
        preds = list(G.predecessors(node))
        if not preds:
            memo[node] = [node]
            return memo[node]
        longest_pred_path = max((longest_path_to(p) for p in preds), key=len)
        memo[node] = longest_pred_path + [node]
        return memo[node]

    for node in G.nodes():
        chain = longest_path_to(node)
        try:
            prod_index = next(i for i, n in enumerate(chain) if n.endswith('_Prod'))
            chain_length = len(chain) - prod_index - 1
        except StopIteration:
            chain_length = len(chain) - 1
        longest_chains[node] = {
            'longest_chain_length': max(0, chain_length),
            'longest_chain': chain
        }

    return longest_chains

def propagate_gas_mix(flow_dict, cost_dict, chain_info):
    """Propagate gas and transport costs through the network by chain level."""
    node_inflows = defaultdict(list)
    max_depth = max(info['longest_chain_length'] for info in chain_info.values())

    # First: add all _Prod flows
    for (src, dst), flow in flow_dict.items():
        if src.endswith('_Prod'):
            cost = cost_dict.get((src, dst), 0)
            node_inflows[dst].append({
                'origin': src,
                'flow': flow,
                'gas_cost': cost,
                'transport_cost': 0
            })

    # Process by depth
    for depth in range(1, max_depth + 1):
        nodes_at_depth = [node for node, info in chain_info.items() if info['longest_chain_length'] == depth]

        for node in nodes_at_depth:
            inflows = node_inflows[node]
            total_inflow = sum(i['flow'] for i in inflows)
            if total_inflow == 0:
                continue

            for (src, dst), flow in flow_dict.items():
                if src != node:
                    continue

                for entry in inflows:
                    share = entry['flow'] / total_inflow if total_inflow > 0 else 0
                    proportional_flow = share * flow
                    cost = cost_dict.get((src, dst), 0)

                    node_inflows[dst].append({
                        'origin': entry['origin'],
                        'flow': proportional_flow,
                        'gas_cost': entry['gas_cost'],
                        'transport_cost': entry['transport_cost'] + cost
                    })

    return node_inflows

def aggregate_node_costs(node_inflows):
    """Aggregate weighted gas and transport costs per node."""
    results = []

    for node, inflows in node_inflows.items():
        total_flow = sum(i['flow'] for i in inflows)
        if total_flow == 0:
            continue

        weighted_gas_cost = sum(i['flow'] * i['gas_cost'] for i in inflows) / total_flow
        weighted_transport_cost = sum(i['flow'] * i['transport_cost'] for i in inflows) / total_flow

        results.append({
            'Node': node,
            'Total Flow': total_flow,
            'Gas Cost': weighted_gas_cost,
            'Transport Cost': weighted_transport_cost,
            'Total Cost': weighted_gas_cost + weighted_transport_cost
        })

    return pd.DataFrame(results).sort_values('Node').reset_index(drop=True)

def compute_average_costs(df_flows, df_edges, commodity='Methane'):
    """Main function to compute gas and transport costs per node."""
    df_flows = preprocess_flows(df_flows, commodity)
    flow_dict, cost_dict = build_flow_and_cost_dicts(df_flows, df_edges, commodity)
    chain_info = get_longest_chain_before_nodes(df_flows, commodity)
    node_inflows = propagate_gas_mix(flow_dict, cost_dict, chain_info)
    return aggregate_node_costs(node_inflows)

def preprocess_flows(df_flows, commodity):
    df_flows = df_flows[df_flows['Commodity'] == commodity].copy()
    df_flows['Edge'] = df_flows['Edge'].apply(ast.literal_eval)
    return df_flows

def build_flow_and_cost_dicts(df_flows, df_edges, commodity):
    flow_dict = defaultdict(float)
    for _, row in df_flows.iterrows():
        flow_dict[row['Edge']] += row['Flow']

    cost_dict = {}
    for _, row in df_edges[df_edges['Commodity'] == commodity].iterrows():
        cost_dict[(row['Source'], row['Destination'])] = row['costs_edge']

    return flow_dict, cost_dict

def compute_longest_chain_lengths(flow_dict):
    predecessors = defaultdict(list)
    for (src, dst) in flow_dict:
        predecessors[dst].append(src)

    longest_paths = {}

    def dfs(node):
        if node in longest_paths:
            return longest_paths[node]
        max_depth = 0
        for pred in predecessors[node]:
            if pred.endswith('_Prod'):
                depth = 1
            else:
                depth = dfs(pred) + 1
            max_depth = max(max_depth, depth)
        longest_paths[node] = max_depth
        return max_depth

    all_nodes = set([dst for _, dst in flow_dict.keys()] + [src for src, _ in flow_dict.keys()])
    for node in all_nodes:
        if node not in longest_paths:
            dfs(node)

    return longest_paths

def propagate_gas_mix_by_level(flow_dict, cost_dict, longest_paths):
    node_inflows = defaultdict(list)

    max_level = max(longest_paths.values())

    for (src, dst), flow in flow_dict.items():
        if src.endswith('_Prod'):
            cost = cost_dict.get((src, dst), 0)
            node_inflows[dst].append({
                'origin': src,
                'flow': flow,
                'gas_cost': cost,
                'transport_cost': 0
            })

    for level in range(1, max_level + 1):
        for node, node_level in longest_paths.items():
            if node_level != level:
                continue

            inflows = node_inflows.get(node, [])
            total_inflow = sum(i['flow'] for i in inflows)
            if total_inflow == 0:
                continue

            for (src, dst), flow in flow_dict.items():
                if src != node:
                    continue

                cost = cost_dict.get((src, dst), 0)
                for entry in inflows:
                    share = entry['flow'] / total_inflow if total_inflow > 0 else 0
                    proportional_flow = share * flow

                    node_inflows[dst].append({
                        'origin': entry['origin'],
                        'flow': proportional_flow,
                        'gas_cost': entry['gas_cost'],
                        'transport_cost': entry['transport_cost'] + cost
                    })

    return node_inflows

def aggregate_node_costs(node_inflows):
    results = []

    for node, inflows in node_inflows.items():
        total_flow = sum(i['flow'] for i in inflows)
        if total_flow == 0:
            continue

        weighted_gas_cost = sum(i['flow'] * i['gas_cost'] for i in inflows) / total_flow
        weighted_transport_cost = sum(i['flow'] * i['transport_cost'] for i in inflows) / total_flow

        results.append({
            'Node': node,
            'Total Flow': total_flow,
            'Gas Cost': weighted_gas_cost,
            'Transport Cost': weighted_transport_cost,
            'Total Cost': weighted_gas_cost + weighted_transport_cost
        })

    return pd.DataFrame(results).sort_values('Node').reset_index(drop=True)

def compute_source_shares(node_inflows):
    """Compute source shares per destination node."""
    share_data = []

    for node, inflows in node_inflows.items():
        total_flow = sum(i['flow'] for i in inflows)
        if total_flow == 0:
            continue

        origin_flows = defaultdict(float)
        for i in inflows:
            origin_flows[i['origin']] += i['flow']

        for origin, flow in origin_flows.items():
            share_data.append({
                'Node': node,
                'Origin': origin,
                'Flow': flow,
                'Share': flow / total_flow
            })

    return pd.DataFrame(share_data).sort_values(['Node', 'Origin']).reset_index(drop=True)

def compute_average_costs(df_flows, df_edges, commodity='Methane'):
    df_flows = preprocess_flows(df_flows, commodity)
    flow_dict, cost_dict = build_flow_and_cost_dicts(df_flows, df_edges, commodity)
    longest_paths = compute_longest_chain_lengths(flow_dict)
    node_inflows = propagate_gas_mix_by_level(flow_dict, cost_dict, longest_paths)
    return aggregate_node_costs(node_inflows), compute_source_shares(node_inflows)

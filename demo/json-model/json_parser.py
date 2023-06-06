'''Demonstration for parsing JSON tree model file generated by XGBoost.  The
support is experimental, output schema is subject to change in the future.
'''
import json
import argparse


class Tree:
    '''A tree built by XGBoost.'''
    # Index into node array
    _left = 0
    _right = 1
    _parent = 2
    _ind = 3
    _cond = 4
    _default_left = 5
    # Index into stat array
    _loss_chg = 0
    _sum_hess = 1
    _base_weight = 2
    _child_cnt = 3

    def __init__(self, tree_id: int, nodes, stats):
        self.tree_id = tree_id
        self.nodes = nodes
        self.stats = stats

    def loss_change(self, node_id: int):
        '''Loss gain of a node.'''
        return self.stats[node_id][self._loss_chg]

    def sum_hessian(self, node_id: int):
        '''Sum Hessian of a node.'''
        return self.stats[node_id][self._sum_hess]

    def base_weight(self, node_id: int):
        '''Base weight of a node.'''
        return self.stats[node_id][self._base_weight]

    def num_children(self, node_id: int):
        '''Number of children of a node.'''
        return self.stats[node_id][self._child_cnt]

    def split_index(self, node_id: int):
        '''Split feature index of node.'''
        return self.nodes[node_id][self._ind]

    def split_condition(self, node_id: int):
        '''Split value of a node.'''
        return self.nodes[node_id][self._cond]

    def parent(self, node_id: int):
        '''Parent ID of a node.'''
        return self.nodes[node_id][self._parent]

    def left_child(self, node_id: int):
        '''Left child ID of a node.'''
        return self.nodes[node_id][self._left]

    def right_child(self, node_id: int):
        '''Right child ID of a node.'''
        return self.nodes[node_id][self._right]

    def is_leaf(self, node_id: int):
        '''Whether a node is leaf.'''
        return self.nodes[node_id][self._left] == -1

    def is_deleted(self, node_id: int):
        '''Whether a node is deleted.'''
        # std::numeric_limits<uint32_t>::max()
        return self.nodes[node_id][self._ind] == 4294967295

    def __str__(self):
        stacks = [0]
        nodes = []
        while stacks:
            nid = stacks.pop()

            node = {'node id': nid, 'gain': self.loss_change(nid)}
            node['cover'] = self.sum_hessian(nid)
            nodes.append(node)

            if not self.is_leaf(nid) and not self.is_deleted(nid):
                left = self.left_child(nid)
                right = self.right_child(nid)
                stacks.append(left)
                stacks.append(right)

        return '\n'.join(map(lambda x: f'  {str(x)}', nodes))


class Model:
    '''Gradient boosted tree model.'''
    def __init__(self, m: dict):
        '''Construct the Model from JSON object.

         parameters
         ----------
          m: A dictionary loaded by json
        '''
        # Basic property of a model
        self.learner_model_shape = model['learner']['learner_model_param']
        self.num_output_group = int(self.learner_model_shape['num_class'])
        self.num_feature = int(self.learner_model_shape['num_feature'])
        self.base_score = float(self.learner_model_shape['base_score'])
        # A field encoding which output group a tree belongs
        self.tree_info = model['learner']['gradient_booster']['model'][
            'tree_info']

        model_shape = model['learner']['gradient_booster']['model'][
            'gbtree_model_param']

        # JSON representation of trees
        j_trees = model['learner']['gradient_booster']['model']['trees']

        # Load the trees
        self.num_trees = int(model_shape['num_trees'])
        self.leaf_size = int(model_shape['size_leaf_vector'])
        # Right now XGBoost doesn't support vector leaf yet
        assert self.leaf_size == 0, str(self.leaf_size)

        trees = []
        for i in range(self.num_trees):
            tree = j_trees[i]
            tree_id = int(tree['id'])
            assert tree_id == i, (tree_id, i)
            # properties
            left_children = tree['left_children']
            right_children = tree['right_children']
            parents = tree['parents']
            split_conditions = tree['split_conditions']
            split_indices = tree['split_indices']
            default_left = tree['default_left']
            # stats
            base_weights = tree['base_weights']
            loss_changes = tree['loss_changes']
            sum_hessian = tree['sum_hessian']
            leaf_child_counts = tree['leaf_child_counts']

            stats = []
            nodes = []
            # We resemble the structure used inside XGBoost, which is similar
            # to adjacency list.
            for node_id in range(len(left_children)):
                nodes.append([
                    left_children[node_id], right_children[node_id],
                    parents[node_id], split_indices[node_id],
                    split_conditions[node_id], default_left[node_id]
                ])
                stats.append([
                    loss_changes[node_id], sum_hessian[node_id],
                    base_weights[node_id], leaf_child_counts[node_id]
                ])

            tree = Tree(tree_id, nodes, stats)
            trees.append(tree)

        self.trees = trees

    def print_model(self):
        for i, tree in enumerate(self.trees):
            print('tree_id:', i)
            print(tree)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demonstration for loading and printing XGBoost model.')
    parser.add_argument('--model',
                        type=str,
                        required=True,
                        help='Path to JSON model file.')
    args = parser.parse_args()
    with open(args.model, 'r') as fd:
        model = json.load(fd)
    model = Model(model)
    model.print_model()

// Builds a forest of family graphs from the full pantheon graph. Parent/child
// direction determines the top of each family; non-genealogical relations are
// retained as connections without making their targets look like children.

function find(parent, x) {
  while (parent[x] !== x) {
    parent[x] = parent[parent[x]];
    x = parent[x];
  }
  return x;
}

function union(parent, a, b) {
  const ra = find(parent, a);
  const rb = find(parent, b);
  if (ra !== rb) parent[ra] = rb;
}

export function buildForest(nodes, edges) {
  const parent = {};
  nodes.forEach((n) => { parent[n.id] = n.id; });
  edges.forEach((e) => {
    if (parent[e.source] !== undefined && parent[e.target] !== undefined) {
      union(parent, e.source, e.target);
    }
  });

  const groups = {};
  nodes.forEach((n) => {
    const root = find(parent, n.id);
    (groups[root] = groups[root] || []).push(n);
  });

  // Undirected adjacency with relation labels, for BFS.
  const adjacency = {};
  nodes.forEach((n) => { adjacency[n.id] = []; });
  edges.forEach((e) => {
    if (!adjacency[e.source] || !adjacency[e.target]) return;
    adjacency[e.source].push({ to: e.target, relation: e.relation });
    adjacency[e.target].push({ to: e.source, relation: e.relation });
  });

  const nodeById = {};
  nodes.forEach((n) => { nodeById[n.id] = n; });

  const clusters = [];
  const isolated = [];

  Object.values(groups).forEach((members) => {
    if (members.length <= 1) {
      isolated.push(...members);
      return;
    }

    const memberIds = new Set(members.map((member) => member.id));
    const hasParent = new Set(
      edges
        .filter((edge) => edge.relation === 'parent_of' && memberIds.has(edge.source) && memberIds.has(edge.target))
        .map((edge) => edge.target)
    );
    const roots = members.filter((member) => !hasParent.has(member.id));
    const root = [...(roots.length ? roots : members)].sort((a, b) => {
      if (a.id === 'Chaos') return -1;
      if (b.id === 'Chaos') return 1;
      return (b.degree || 0) - (a.degree || 0);
    })[0];
    const visited = new Set([root.id]);
    const levels = [[root]];
    const treeEdges = [];
    let frontier = [root.id];

    while (frontier.length > 0) {
      const next = [];
      const nextNodes = [];
      frontier.forEach((id) => {
        (adjacency[id] || []).forEach(({ to, relation }) => {
          if (visited.has(to) || !nodeById[to]) return;
          visited.add(to);
          treeEdges.push({ parentId: id, childId: to, relation });
          next.push(to);
          nextNodes.push(nodeById[to]);
        });
      });
      if (nextNodes.length > 0) levels.push(nextNodes);
      frontier = next;
    }

    clusters.push({ id: root.id, root, levels, edges: treeEdges, size: members.length });
  });

  clusters.sort((a, b) => b.size - a.size);
  isolated.sort((a, b) => a.id.localeCompare(b.id));

  return { clusters, isolated };
}

export const PANTHEON_ROOT_ID = '__pantheon_root__';

/**
 * Merges every cluster from `buildForest` into a single tree by hanging
 * each cluster's own root off one shared, clearly-labeled organizing node.
 * This is NOT a claim that the myths connect every figure to every other —
 * the 19 family groups genuinely don't overlap in the source material — it
 * just gives one diagram instead of nineteen, with the synthetic root
 * rendered distinctly so it reads as "here are the pantheon's branches,"
 * not as a god or ancestor.
 */
export function buildUnifiedTree(nodes, edges) {
  const { clusters, isolated } = buildForest(nodes, edges);

  const root = {
    id: PANTHEON_ROOT_ID,
    label: 'The Pantheon',
    type: 'root',
    degree: clusters.length,
    myths: [],
  };

  const maxDepth = Math.max(0, ...clusters.map((c) => c.levels.length));
  const levels = [[root], clusters.map((c) => c.root)];
  for (let depth = 1; depth < maxDepth; depth += 1) {
    const row = clusters.flatMap((c) => c.levels[depth] || []);
    if (row.length > 0) levels.push(row);
  }

  const treeEdges = [
    ...clusters.map((c) => ({ parentId: root.id, childId: c.root.id, relation: 'family group' })),
    ...clusters.flatMap((c) => c.edges),
  ];

  return {
    tree: { id: root.id, root, levels, edges: treeEdges, size: nodes.length - isolated.length },
    isolated,
    clusterCount: clusters.length,
  };
}

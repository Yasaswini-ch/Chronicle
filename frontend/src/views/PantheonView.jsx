import React, { useEffect, useMemo, useState } from 'react';
import PageHeader from '../components/PageHeader';
import CoreTree from '../components/CoreTree';
import { THEME } from '../data/theme';
import './PantheonView.css';

const FAMILY_OPTIONS = [
  { id: 'primordials', label: 'Primordial Deities', names: ['Chaos', 'Gaia', 'Uranus', 'Nyx', 'Erebus', 'Tartarus', 'Eros', 'Aether', 'Hemera'] },
  { id: 'titans', label: 'Titans', names: ['Cronus', 'Rhea', 'Oceanus', 'Tethys', 'Hyperion', 'Theia', 'Iapetus', 'Themis', 'Mnemosyne', 'Phoebe', 'Coeus', 'Crius'] },
  { id: 'olympians', label: 'Olympian Gods', names: ['Zeus', 'Hera', 'Poseidon', 'Hades', 'Demeter', 'Hestia', 'Athena', 'Apollo', 'Artemis', 'Ares', 'Hermes', 'Aphrodite', 'Dionysus', 'Hephaestus'] },
  { id: 'heroes', label: 'Heroes', names: ['Heracles', 'Perseus', 'Theseus', 'Jason', 'Achilles', 'Odysseus', 'Orpheus', 'Bellerophon', 'Atalanta', 'Meleager'] },
  { id: 'mortals', label: 'Mortals & Others', names: ['Leda', 'Helen', 'Castor', 'Pollux', 'Clytemnestra', 'Tyndareus', 'Daphne', 'Midas', 'Sisyphus', 'Psyche'] },
];

export default function PantheonView({ onSelectMyth, initialName, subTabs }) {
  const [graphData, setGraphData] = useState({ nodes: [], edges: [] });
  const [selectedFigure, setSelectedFigure] = useState(null);
  const [activeFamily, setActiveFamily] = useState(null);

  useEffect(() => {
    fetch('/api/graph')
      .then((res) => res.json())
      .then((data) => {
        setGraphData(data);
        const requested = initialName && (data.nodes || []).find(
          (node) => (node.label || node.id).toLowerCase() === initialName.toLowerCase()
        );
        if (requested) setSelectedFigure(requested);
        const requestedFamily = FAMILY_OPTIONS.find((family) => family.names.includes(requested?.label || requested?.id));
        if (requestedFamily) setActiveFamily(requestedFamily.id);
      })
      .catch((err) => console.error('Failed to load graph:', err));
  }, [initialName]);

  const availableFamilies = useMemo(() => FAMILY_OPTIONS.map((family) => ({
    ...family,
    members: family.names
      .map((name) => graphData.nodes.find((node) => (node.label || node.id).toLowerCase() === name.toLowerCase()))
      .filter(Boolean),
  })).filter((family) => family.members.length > 0), [graphData.nodes]);

  const chooseFamily = (family) => {
    setActiveFamily(family.id);
    if (family.members[0]) setSelectedFigure(family.members[0]);
  };

  return (
    <div className="page-surface pantheon-page-surface">
      <PageHeader
        label="FAMILY TREE"
        title="A family written in the stars"
        intro="Explore the divine lineages and mythological relationships that shaped the ancient world. Choose any figure to see their family and profile."
        image={THEME.treeBg}
      >
        {subTabs}
      </PageHeader>

      <div className="section-parchment pantheon-parchment">
        <div className="pantheon-parchment-layout">
          <aside className="pantheon-directory" aria-label="Figure directory">
            <div className="pantheon-directory-kicker">Explore by family</div>
            <div className="pantheon-directory-list">
              {availableFamilies.map((family) => (
                <button key={family.id} type="button" className={activeFamily === family.id ? 'active' : ''} onClick={() => chooseFamily(family)}>
                  <span>{family.label}</span><small>{family.members.length}</small>
                </button>
              ))}
            </div>
          </aside>

          <main className="pantheon-core-column">
            <div className="pantheon-section-heading">
              <div className="label">FAMILY TREE</div>
              <p>
                Choose a figure to reveal their family tree. The tree stays hidden until you ask for a
                specific figure.
              </p>
            </div>
            <CoreTree
              nodes={graphData.nodes}
              edges={graphData.edges}
              selectedId={selectedFigure?.id}
              onSelect={setSelectedFigure}
              onNodeClick={(node) => {
                window.location.hash = `/explore/figures/${encodeURIComponent(node.label || node.id)}`;
              }}
            />
          </main>
        </div>
      </div>
    </div>
  );
}
